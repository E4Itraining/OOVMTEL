"""
User Feedback Module.

Provides feedback collection and analysis for the SYNAPSIX AI assistant,
enabling continuous improvement based on user interactions.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Types of feedback."""
    RATING = "rating"           # Simple thumbs up/down or star rating
    CORRECTION = "correction"   # User corrects the response
    PREFERENCE = "preference"   # User indicates preference
    BUG_REPORT = "bug_report"  # Something went wrong
    SUGGESTION = "suggestion"   # Feature suggestion


class FeedbackSentiment(str, Enum):
    """Sentiment of feedback."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class FeedbackEntry:
    """A single feedback entry."""
    id: str
    session_id: str
    message_id: str
    feedback_type: FeedbackType
    sentiment: FeedbackSentiment
    rating: Optional[int] = None  # 1-5 or boolean (0/1)
    comment: Optional[str] = None
    correction: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    intent: Optional[str] = None
    query: Optional[str] = None
    response_snippet: Optional[str] = None


@dataclass
class FeedbackStats:
    """Aggregated feedback statistics."""
    total_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    average_rating: float = 0.0
    satisfaction_rate: float = 0.0
    common_issues: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class FeedbackCollector:
    """
    Collects and stores user feedback.

    Features:
    - Simple thumbs up/down
    - Detailed ratings
    - Correction suggestions
    - Issue reporting
    """

    def __init__(self, max_entries: int = 10000):
        """
        Initialize the feedback collector.

        Args:
            max_entries: Maximum feedback entries to store
        """
        self.max_entries = max_entries
        self._entries: List[FeedbackEntry] = []
        self._entry_index: Dict[str, FeedbackEntry] = {}

    def submit_rating(
        self,
        session_id: str,
        message_id: str,
        is_positive: bool,
        query: Optional[str] = None,
        response: Optional[str] = None,
        intent: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit a simple thumbs up/down rating.

        Args:
            session_id: Session identifier
            message_id: Message being rated
            is_positive: True for positive, False for negative
            query: The user's original query
            response: The assistant's response (snippet)
            intent: Detected intent
            user_id: Optional user identifier

        Returns:
            Feedback entry ID
        """
        entry = FeedbackEntry(
            id=self._generate_id(session_id, message_id),
            session_id=session_id,
            message_id=message_id,
            feedback_type=FeedbackType.RATING,
            sentiment=FeedbackSentiment.POSITIVE if is_positive else FeedbackSentiment.NEGATIVE,
            rating=1 if is_positive else 0,
            query=query,
            response_snippet=response[:200] if response else None,
            intent=intent,
            user_id=user_id
        )

        return self._store_entry(entry)

    def submit_detailed_rating(
        self,
        session_id: str,
        message_id: str,
        rating: int,
        comment: Optional[str] = None,
        categories: Optional[List[str]] = None,
        query: Optional[str] = None,
        intent: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit a detailed rating (1-5 stars).

        Args:
            session_id: Session identifier
            message_id: Message being rated
            rating: Rating from 1 to 5
            comment: Optional comment
            categories: Categories the feedback applies to
            query: The user's original query
            intent: Detected intent
            user_id: Optional user identifier

        Returns:
            Feedback entry ID
        """
        rating = max(1, min(5, rating))

        sentiment = FeedbackSentiment.POSITIVE if rating >= 4 else \
                   FeedbackSentiment.NEGATIVE if rating <= 2 else \
                   FeedbackSentiment.NEUTRAL

        entry = FeedbackEntry(
            id=self._generate_id(session_id, message_id),
            session_id=session_id,
            message_id=message_id,
            feedback_type=FeedbackType.RATING,
            sentiment=sentiment,
            rating=rating,
            comment=comment,
            query=query,
            intent=intent,
            user_id=user_id,
            context={"categories": categories} if categories else {}
        )

        return self._store_entry(entry)

    def submit_correction(
        self,
        session_id: str,
        message_id: str,
        correction: str,
        original_response: str,
        query: Optional[str] = None,
        intent: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit a correction for an incorrect response.

        Args:
            session_id: Session identifier
            message_id: Message being corrected
            correction: The correct information
            original_response: The original incorrect response
            query: The user's original query
            intent: Detected intent
            user_id: Optional user identifier

        Returns:
            Feedback entry ID
        """
        entry = FeedbackEntry(
            id=self._generate_id(session_id, message_id),
            session_id=session_id,
            message_id=message_id,
            feedback_type=FeedbackType.CORRECTION,
            sentiment=FeedbackSentiment.NEGATIVE,
            correction=correction,
            response_snippet=original_response[:500],
            query=query,
            intent=intent,
            user_id=user_id
        )

        return self._store_entry(entry)

    def submit_bug_report(
        self,
        session_id: str,
        message_id: str,
        description: str,
        expected_behavior: Optional[str] = None,
        query: Optional[str] = None,
        intent: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit a bug report.

        Args:
            session_id: Session identifier
            message_id: Related message
            description: Bug description
            expected_behavior: What should have happened
            query: The user's original query
            intent: Detected intent
            user_id: Optional user identifier

        Returns:
            Feedback entry ID
        """
        entry = FeedbackEntry(
            id=self._generate_id(session_id, message_id),
            session_id=session_id,
            message_id=message_id,
            feedback_type=FeedbackType.BUG_REPORT,
            sentiment=FeedbackSentiment.NEGATIVE,
            comment=description,
            query=query,
            intent=intent,
            user_id=user_id,
            context={"expected_behavior": expected_behavior} if expected_behavior else {}
        )

        return self._store_entry(entry)

    def submit_suggestion(
        self,
        session_id: str,
        suggestion: str,
        category: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Submit a feature suggestion.

        Args:
            session_id: Session identifier
            suggestion: The suggestion text
            category: Category of suggestion
            user_id: Optional user identifier

        Returns:
            Feedback entry ID
        """
        entry = FeedbackEntry(
            id=self._generate_id(session_id, "suggestion"),
            session_id=session_id,
            message_id="",
            feedback_type=FeedbackType.SUGGESTION,
            sentiment=FeedbackSentiment.NEUTRAL,
            comment=suggestion,
            user_id=user_id,
            context={"category": category} if category else {}
        )

        return self._store_entry(entry)

    def _generate_id(self, session_id: str, message_id: str) -> str:
        """Generate a unique feedback ID."""
        content = f"{session_id}:{message_id}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _store_entry(self, entry: FeedbackEntry) -> str:
        """Store a feedback entry."""
        self._entries.append(entry)
        self._entry_index[entry.id] = entry

        # Cleanup if needed
        if len(self._entries) > self.max_entries:
            old_entry = self._entries.pop(0)
            if old_entry.id in self._entry_index:
                del self._entry_index[old_entry.id]

        logger.info(f"Feedback recorded: {entry.feedback_type.value} - {entry.sentiment.value}")
        return entry.id

    def get_entry(self, feedback_id: str) -> Optional[FeedbackEntry]:
        """Get a feedback entry by ID."""
        return self._entry_index.get(feedback_id)

    def get_recent(self, limit: int = 50) -> List[FeedbackEntry]:
        """Get recent feedback entries."""
        return self._entries[-limit:]


class FeedbackAnalyzer:
    """
    Analyzes feedback to identify patterns and improvement areas.

    Features:
    - Satisfaction rate calculation
    - Common issue identification
    - Intent-specific analysis
    - Trend detection
    """

    def __init__(self, collector: FeedbackCollector):
        """
        Initialize the analyzer.

        Args:
            collector: FeedbackCollector instance
        """
        self.collector = collector

    def get_stats(
        self,
        time_range: Optional[timedelta] = None,
        intent_filter: Optional[str] = None
    ) -> FeedbackStats:
        """
        Get aggregated feedback statistics.

        Args:
            time_range: Filter by time range (e.g., last 24 hours)
            intent_filter: Filter by specific intent

        Returns:
            FeedbackStats object
        """
        entries = self._filter_entries(time_range, intent_filter)

        if not entries:
            return FeedbackStats()

        # Count sentiments
        positive = sum(1 for e in entries if e.sentiment == FeedbackSentiment.POSITIVE)
        negative = sum(1 for e in entries if e.sentiment == FeedbackSentiment.NEGATIVE)
        neutral = sum(1 for e in entries if e.sentiment == FeedbackSentiment.NEUTRAL)

        # Calculate average rating
        rated = [e for e in entries if e.rating is not None and e.rating > 0]
        avg_rating = sum(e.rating for e in rated) / len(rated) if rated else 0.0

        # Satisfaction rate
        satisfaction = positive / len(entries) if entries else 0.0

        # Identify common issues from negative feedback
        issues = self._extract_common_issues(entries)

        # Get improvement suggestions
        suggestions = self._extract_suggestions(entries)

        return FeedbackStats(
            total_count=len(entries),
            positive_count=positive,
            negative_count=negative,
            neutral_count=neutral,
            average_rating=avg_rating,
            satisfaction_rate=satisfaction,
            common_issues=issues,
            improvement_suggestions=suggestions,
            period_start=entries[0].timestamp if entries else None,
            period_end=entries[-1].timestamp if entries else None
        )

    def get_intent_breakdown(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, FeedbackStats]:
        """
        Get feedback statistics broken down by intent.

        Args:
            time_range: Filter by time range

        Returns:
            Dictionary of intent -> FeedbackStats
        """
        entries = self._filter_entries(time_range, None)

        # Group by intent
        by_intent: Dict[str, List[FeedbackEntry]] = {}
        for entry in entries:
            intent = entry.intent or "unknown"
            if intent not in by_intent:
                by_intent[intent] = []
            by_intent[intent].append(entry)

        # Calculate stats for each intent
        result = {}
        for intent, intent_entries in by_intent.items():
            positive = sum(1 for e in intent_entries if e.sentiment == FeedbackSentiment.POSITIVE)

            result[intent] = FeedbackStats(
                total_count=len(intent_entries),
                positive_count=positive,
                negative_count=sum(1 for e in intent_entries if e.sentiment == FeedbackSentiment.NEGATIVE),
                neutral_count=sum(1 for e in intent_entries if e.sentiment == FeedbackSentiment.NEUTRAL),
                satisfaction_rate=positive / len(intent_entries) if intent_entries else 0
            )

        return result

    def get_trend(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get satisfaction trend over time.

        Args:
            days: Number of days to analyze

        Returns:
            List of daily stats
        """
        trend = []
        now = datetime.utcnow()

        for i in range(days):
            day_start = now - timedelta(days=i+1)
            day_end = now - timedelta(days=i)

            day_entries = [
                e for e in self.collector._entries
                if day_start <= e.timestamp < day_end
            ]

            if day_entries:
                positive = sum(1 for e in day_entries if e.sentiment == FeedbackSentiment.POSITIVE)
                satisfaction = positive / len(day_entries)
            else:
                satisfaction = None

            trend.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": len(day_entries),
                "satisfaction_rate": satisfaction
            })

        return list(reversed(trend))

    def get_corrections(
        self,
        limit: int = 20,
        intent_filter: Optional[str] = None
    ) -> List[FeedbackEntry]:
        """
        Get user corrections for learning.

        Args:
            limit: Maximum corrections to return
            intent_filter: Filter by intent

        Returns:
            List of correction entries
        """
        entries = [
            e for e in self.collector._entries
            if e.feedback_type == FeedbackType.CORRECTION
        ]

        if intent_filter:
            entries = [e for e in entries if e.intent == intent_filter]

        return entries[-limit:]

    def get_problematic_queries(
        self,
        min_negative_count: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Identify queries that frequently receive negative feedback.

        Args:
            min_negative_count: Minimum negative count to include

        Returns:
            List of problematic query patterns
        """
        # Group by query similarity (simplified: exact match for now)
        query_feedback: Dict[str, List[FeedbackEntry]] = {}

        for entry in self.collector._entries:
            if entry.query:
                query_key = entry.query.lower().strip()
                if query_key not in query_feedback:
                    query_feedback[query_key] = []
                query_feedback[query_key].append(entry)

        # Find problematic queries
        problematic = []
        for query, entries in query_feedback.items():
            negative_count = sum(1 for e in entries if e.sentiment == FeedbackSentiment.NEGATIVE)
            if negative_count >= min_negative_count:
                problematic.append({
                    "query": query,
                    "total_count": len(entries),
                    "negative_count": negative_count,
                    "negative_rate": negative_count / len(entries),
                    "sample_corrections": [
                        e.correction for e in entries
                        if e.correction
                    ][:3]
                })

        return sorted(problematic, key=lambda x: x["negative_count"], reverse=True)

    def _filter_entries(
        self,
        time_range: Optional[timedelta],
        intent_filter: Optional[str]
    ) -> List[FeedbackEntry]:
        """Filter entries by time range and intent."""
        entries = self.collector._entries

        if time_range:
            cutoff = datetime.utcnow() - time_range
            entries = [e for e in entries if e.timestamp >= cutoff]

        if intent_filter:
            entries = [e for e in entries if e.intent == intent_filter]

        return entries

    def _extract_common_issues(self, entries: List[FeedbackEntry]) -> List[str]:
        """Extract common issues from negative feedback."""
        issues = []
        negative = [e for e in entries if e.sentiment == FeedbackSentiment.NEGATIVE]

        # Simple keyword extraction from comments
        issue_keywords = {
            "incorrect": "Réponses incorrectes",
            "slow": "Temps de réponse lent",
            "confusing": "Réponses confuses",
            "incomplete": "Informations incomplètes",
            "error": "Erreurs techniques",
            "wrong": "Données erronées",
            "missing": "Données manquantes",
            "outdated": "Informations obsolètes"
        }

        issue_counts: Dict[str, int] = {}
        for entry in negative:
            if entry.comment:
                comment_lower = entry.comment.lower()
                for keyword, issue in issue_keywords.items():
                    if keyword in comment_lower:
                        issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Sort by frequency
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        issues = [issue for issue, count in sorted_issues[:5]]

        return issues

    def _extract_suggestions(self, entries: List[FeedbackEntry]) -> List[str]:
        """Extract improvement suggestions."""
        suggestion_entries = [
            e for e in entries
            if e.feedback_type == FeedbackType.SUGGESTION and e.comment
        ]

        return [e.comment for e in suggestion_entries[-10:]]


class FeedbackReporter:
    """
    Generates feedback reports for monitoring and improvement.
    """

    def __init__(self, analyzer: FeedbackAnalyzer):
        """Initialize the reporter."""
        self.analyzer = analyzer

    def generate_daily_report(self, language: str = "fr") -> str:
        """
        Generate a daily feedback report.

        Args:
            language: Report language

        Returns:
            Formatted report text
        """
        stats = self.analyzer.get_stats(time_range=timedelta(days=1))
        intent_breakdown = self.analyzer.get_intent_breakdown(time_range=timedelta(days=1))

        if language == "fr":
            lines = [
                "# 📊 Rapport de Feedback Quotidien",
                f"_Généré le {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC_",
                "",
                "## Résumé",
                f"- **Total interactions évaluées**: {stats.total_count}",
                f"- **Taux de satisfaction**: {stats.satisfaction_rate:.1%}",
                f"- **Note moyenne**: {stats.average_rating:.1f}/5",
                "",
                "### Répartition",
                f"- 👍 Positifs: {stats.positive_count}",
                f"- 👎 Négatifs: {stats.negative_count}",
                f"- ➖ Neutres: {stats.neutral_count}",
            ]

            if stats.common_issues:
                lines.extend([
                    "",
                    "## Problèmes fréquents",
                ])
                for issue in stats.common_issues:
                    lines.append(f"- {issue}")

            if intent_breakdown:
                lines.extend([
                    "",
                    "## Performance par Intent",
                    "| Intent | Volume | Satisfaction |",
                    "|--------|--------|--------------|"
                ])
                for intent, intent_stats in sorted(
                    intent_breakdown.items(),
                    key=lambda x: x[1].total_count,
                    reverse=True
                ):
                    lines.append(
                        f"| {intent} | {intent_stats.total_count} | {intent_stats.satisfaction_rate:.1%} |"
                    )

            if stats.improvement_suggestions:
                lines.extend([
                    "",
                    "## Suggestions d'amélioration",
                ])
                for suggestion in stats.improvement_suggestions[:5]:
                    lines.append(f"- {suggestion}")
        else:
            lines = [
                "# 📊 Daily Feedback Report",
                f"_Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC_",
                "",
                "## Summary",
                f"- **Total rated interactions**: {stats.total_count}",
                f"- **Satisfaction rate**: {stats.satisfaction_rate:.1%}",
                f"- **Average rating**: {stats.average_rating:.1f}/5",
            ]

        return "\n".join(lines)

    def generate_insights(self, language: str = "fr") -> Dict[str, Any]:
        """
        Generate actionable insights from feedback.

        Returns:
            Dictionary with insights and recommendations
        """
        stats = self.analyzer.get_stats(time_range=timedelta(days=7))
        trend = self.analyzer.get_trend(days=7)
        problematic = self.analyzer.get_problematic_queries()

        # Calculate trend direction
        if len(trend) >= 2:
            recent_avg = sum(
                t.get("satisfaction_rate", 0) or 0
                for t in trend[:3]
            ) / 3
            older_avg = sum(
                t.get("satisfaction_rate", 0) or 0
                for t in trend[4:]
            ) / max(1, len(trend) - 4)
            trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend_direction = "insufficient_data"

        insights = {
            "satisfaction_rate": stats.satisfaction_rate,
            "trend_direction": trend_direction,
            "total_feedback": stats.total_count,
            "common_issues": stats.common_issues,
            "problematic_queries_count": len(problematic),
            "recommendations": []
        }

        # Generate recommendations
        if language == "fr":
            if stats.satisfaction_rate < 0.7:
                insights["recommendations"].append(
                    "Le taux de satisfaction est inférieur à 70%. Analyse approfondie recommandée."
                )
            if problematic:
                insights["recommendations"].append(
                    f"{len(problematic)} types de requêtes reçoivent régulièrement des feedback négatifs."
                )
            if "Réponses incorrectes" in stats.common_issues:
                insights["recommendations"].append(
                    "Améliorer la précision des réponses - nombreux feedback sur données incorrectes."
                )
        else:
            if stats.satisfaction_rate < 0.7:
                insights["recommendations"].append(
                    "Satisfaction rate is below 70%. Deep analysis recommended."
                )
            if problematic:
                insights["recommendations"].append(
                    f"{len(problematic)} query types regularly receive negative feedback."
                )

        return insights


# Global instances
_feedback_collector: Optional[FeedbackCollector] = None
_feedback_analyzer: Optional[FeedbackAnalyzer] = None


def get_feedback_collector() -> FeedbackCollector:
    """Get or create the global feedback collector."""
    global _feedback_collector
    if _feedback_collector is None:
        _feedback_collector = FeedbackCollector()
    return _feedback_collector


def get_feedback_analyzer() -> FeedbackAnalyzer:
    """Get or create the global feedback analyzer."""
    global _feedback_analyzer, _feedback_collector
    if _feedback_analyzer is None:
        _feedback_analyzer = FeedbackAnalyzer(get_feedback_collector())
    return _feedback_analyzer
