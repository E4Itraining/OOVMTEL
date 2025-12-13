"""
NLP Engine - Main conversational analytics engine
Processes natural language queries and generates structured responses
"""

import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import hashlib

from .models import (
    ConversationalQuery,
    QueryIntent,
    ExtractedEntities,
    QueryResult,
    NLPResponse,
    SuggestedVisualization,
    ConversationContext,
    TimeRange,
    VisualizationType,
    DataPoint,
    EQUIPMENT_KEYWORDS,
    METRIC_KEYWORDS,
    TIME_KEYWORDS,
    INTENT_PATTERNS,
)
from .query_generator import QueryGenerator
from .response_builder import ResponseBuilder

logger = logging.getLogger(__name__)


class NLPEngine:
    """
    Main NLP Engine for conversational analytics.

    Features:
    - Language detection (French/English)
    - Intent classification
    - Entity extraction (equipment, metrics, time ranges)
    - Query generation (PromQL, OpenSearch)
    - Response generation with visualizations
    - Context management for follow-up questions
    """

    def __init__(
        self,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
        opensearch_url: str = "http://opensearch:9200",
        llm_endpoint: Optional[str] = None,
        llm_api_key: Optional[str] = None,
    ):
        self.victoria_metrics_url = victoria_metrics_url
        self.opensearch_url = opensearch_url
        self.llm_endpoint = llm_endpoint
        self.llm_api_key = llm_api_key

        self.query_generator = QueryGenerator(victoria_metrics_url, opensearch_url)
        self.response_builder = ResponseBuilder()

        # Session contexts for multi-turn conversations
        self.contexts: Dict[str, ConversationContext] = {}

        # Query cache
        self.query_cache: Dict[str, Tuple[NLPResponse, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)

        logger.info("NLP Engine initialized")

    async def process_query(
        self,
        query: ConversationalQuery,
        metrics_data: Optional[Dict[str, Any]] = None
    ) -> NLPResponse:
        """
        Process a natural language query and return structured response.

        Args:
            query: The conversational query to process
            metrics_data: Optional pre-fetched metrics data

        Returns:
            NLPResponse with answer, visualizations, and suggestions
        """
        start_time = time.time()

        try:
            # Check cache
            cache_key = self._get_cache_key(query)
            if cache_key in self.query_cache:
                cached_response, cached_time = self.query_cache[cache_key]
                if datetime.utcnow() - cached_time < self.cache_ttl:
                    logger.info(f"Cache hit for query: {query.query[:50]}...")
                    return cached_response

            # Detect language
            language = self._detect_language(query.query) if query.language == "auto" else query.language

            # Get or create session context
            context = self._get_context(query.session_id)

            # Extract intent
            intent = self._detect_intent(query.query, language)

            # Extract entities
            entities = self._extract_entities(query.query, language, context)

            # Apply context from previous turns
            entities = self._apply_context(entities, context)

            # Generate and execute queries
            query_results = await self._execute_queries(intent, entities, metrics_data)

            # Build response
            response = self._build_response(
                query=query.query,
                intent=intent,
                entities=entities,
                query_results=query_results,
                language=language,
                metrics_data=metrics_data
            )

            # Update context
            self._update_context(context, query.query, intent, entities, query_results)

            # Calculate processing time
            response.processing_time_ms = (time.time() - start_time) * 1000

            # Cache response
            self.query_cache[cache_key] = (response, datetime.utcnow())

            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return NLPResponse(
                answer=self._get_error_message(str(e), query.language or "fr"),
                intent=QueryIntent.UNKNOWN,
                entities=ExtractedEntities(),
                confidence=0.0,
                processing_time_ms=(time.time() - start_time) * 1000
            )

    def _detect_language(self, text: str) -> str:
        """Detect if text is French or English."""
        french_indicators = [
            "pourquoi", "comment", "quand", "où", "quel", "quelle",
            "est-ce", "qu'est", "aujourd'hui", "hier", "demain",
            "ligne", "machine", "température", "problème", "défaut"
        ]
        english_indicators = [
            "why", "how", "when", "where", "what", "which",
            "is the", "are the", "today", "yesterday", "tomorrow",
            "line", "machine", "temperature", "problem", "defect"
        ]

        text_lower = text.lower()
        french_score = sum(1 for word in french_indicators if word in text_lower)
        english_score = sum(1 for word in english_indicators if word in text_lower)

        return "fr" if french_score >= english_score else "en"

    def _detect_intent(self, query: str, language: str) -> QueryIntent:
        """Detect user intent from query."""
        query_lower = query.lower()

        # Score each intent based on keyword matches
        intent_scores: Dict[QueryIntent, int] = defaultdict(int)

        patterns = INTENT_PATTERNS.get(language, INTENT_PATTERNS["en"])
        for intent, keywords in patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    intent_scores[intent] += 1

        # Default to metrics query if no clear intent
        if not intent_scores:
            return QueryIntent.METRICS_QUERY

        # Return highest scoring intent
        return max(intent_scores, key=intent_scores.get)

    def _extract_entities(
        self,
        query: str,
        language: str,
        context: Optional[ConversationContext] = None
    ) -> ExtractedEntities:
        """Extract entities from natural language query."""
        query_lower = query.lower()
        entities = ExtractedEntities()

        # Extract equipment
        equipment_kw = EQUIPMENT_KEYWORDS.get(language, EQUIPMENT_KEYWORDS["en"])
        for kw, eq_type in equipment_kw.items():
            if kw in query_lower:
                entities.equipment_types.append(eq_type)

        # Extract specific equipment IDs (e.g., "ligne 3", "Pump-003")
        equipment_patterns = [
            r'ligne\s*(\d+)',
            r'line\s*(\d+)',
            r'([A-Za-z]+)-(\d+)',
            r'([A-Za-z]+)\s*#?\s*(\d+)',
        ]
        for pattern in equipment_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    entities.equipment.append("-".join(match))
                else:
                    entities.equipment.append(f"Line-{match}")

        # Extract metrics
        metric_kw = METRIC_KEYWORDS.get(language, METRIC_KEYWORDS["en"])
        for kw, metric in metric_kw.items():
            if kw in query_lower:
                if metric not in entities.metrics:
                    entities.metrics.append(metric)

        # Extract KPIs
        kpi_keywords = ["oee", "trs", "quality", "qualité", "availability", "disponibilité", "performance"]
        for kw in kpi_keywords:
            if kw in query_lower:
                entities.kpis.append(kw)

        # Extract time range
        entities.time_range = self._extract_time_range(query, language)

        # Extract severity levels
        severity_keywords = {
            "critique": "critical", "critical": "critical",
            "warning": "warning", "attention": "warning",
            "info": "info", "information": "info"
        }
        for kw, sev in severity_keywords.items():
            if kw in query_lower:
                entities.severity_levels.append(sev)

        return entities

    def _extract_time_range(self, query: str, language: str) -> Optional[TimeRange]:
        """Extract time range from query."""
        query_lower = query.lower()
        time_kw = TIME_KEYWORDS.get(language, TIME_KEYWORDS["en"])

        now = datetime.utcnow()

        for keyword, (period_type, days_back) in time_kw.items():
            if keyword in query_lower:
                if period_type == "today":
                    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    return TimeRange(start=start, end=now, duration_description=keyword)
                elif period_type == "yesterday":
                    yesterday = now - timedelta(days=1)
                    start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                    end = yesterday.replace(hour=23, minute=59, second=59)
                    return TimeRange(start=start, end=end, duration_description=keyword)
                elif period_type == "this_morning":
                    start = now.replace(hour=6, minute=0, second=0, microsecond=0)
                    end = now.replace(hour=12, minute=0, second=0, microsecond=0)
                    return TimeRange(start=start, end=end, duration_description=keyword)
                elif period_type == "this_afternoon":
                    start = now.replace(hour=12, minute=0, second=0, microsecond=0)
                    end = now.replace(hour=18, minute=0, second=0, microsecond=0)
                    return TimeRange(start=start, end=end, duration_description=keyword)
                else:
                    start = now - timedelta(days=days_back)
                    return TimeRange(start=start, end=now, duration_description=keyword)

        # Check for explicit hour patterns
        hour_pattern = r'(\d+)\s*(h|heures?|hours?)'
        match = re.search(hour_pattern, query_lower)
        if match:
            hours = int(match.group(1))
            return TimeRange.last_hours(hours)

        # Check for explicit day patterns
        day_pattern = r'(\d+)\s*(j|jours?|days?)'
        match = re.search(day_pattern, query_lower)
        if match:
            days = int(match.group(1))
            return TimeRange.last_days(days)

        # Default to last 24 hours
        return TimeRange.last_hours(24)

    def _apply_context(
        self,
        entities: ExtractedEntities,
        context: Optional[ConversationContext]
    ) -> ExtractedEntities:
        """Apply context from previous conversation turns."""
        if not context:
            return entities

        # If no equipment specified, use equipment from context
        if not entities.equipment and context.equipment_context:
            entities.equipment = context.equipment_context.copy()

        # If no time range specified, use time from context
        if not entities.time_range and context.time_context:
            entities.time_range = context.time_context

        # Merge with previous entities if this looks like a follow-up
        if context.last_entities:
            if not entities.metrics and context.last_entities.metrics:
                entities.metrics = context.last_entities.metrics.copy()

        return entities

    async def _execute_queries(
        self,
        intent: QueryIntent,
        entities: ExtractedEntities,
        metrics_data: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """Execute queries based on intent and entities."""
        results = []

        # If we have pre-fetched metrics data, use it
        if metrics_data:
            result = self._query_from_metrics_data(intent, entities, metrics_data)
            if result:
                results.append(result)

        # Generate and execute PromQL queries
        promql_queries = self.query_generator.generate_promql(intent, entities)
        for query_info in promql_queries:
            result = await self._execute_promql(query_info)
            if result:
                results.append(result)

        return results

    def _query_from_metrics_data(
        self,
        intent: QueryIntent,
        entities: ExtractedEntities,
        metrics_data: Dict[str, Any]
    ) -> Optional[QueryResult]:
        """Extract relevant data from pre-fetched metrics."""
        try:
            data_points = []
            business = metrics_data.get("business", {})
            tech = metrics_data.get("tech", {})

            # Handle different intents
            if intent in [QueryIntent.METRICS_QUERY, QueryIntent.SUMMARY]:
                # Extract requested metrics
                for metric in entities.metrics or ["oee"]:
                    value = None
                    if metric == "oee":
                        value = business.get("oee")
                    elif metric == "quality_rate":
                        value = business.get("quality_rate")
                    elif metric == "availability":
                        value = business.get("availability")
                    elif metric == "performance":
                        value = business.get("performance")
                    elif metric == "production_count":
                        value = business.get("production_today")
                    elif metric == "defects":
                        value = business.get("defects_today")
                    elif metric == "cycle_time":
                        value = business.get("cycle_time")

                    if value is not None:
                        data_points.append(DataPoint(
                            timestamp=datetime.utcnow(),
                            value=value,
                            metric=metric
                        ))

            elif intent == QueryIntent.EQUIPMENT_STATUS:
                equipment_list = business.get("equipment", [])
                for eq in equipment_list:
                    # Filter by requested equipment if specified
                    if entities.equipment:
                        if not any(e.lower() in eq.get("name", "").lower() for e in entities.equipment):
                            continue
                    data_points.append(DataPoint(
                        timestamp=datetime.utcnow(),
                        value=eq.get("status", "unknown"),
                        metric="equipment_status",
                        labels={"name": eq.get("name", ""), "temp": str(eq.get("temp", 0))}
                    ))

            elif intent == QueryIntent.ALERT_STATUS:
                alarms = business.get("alarms", [])
                for alarm in alarms:
                    if entities.severity_levels:
                        if alarm.get("severity") not in entities.severity_levels:
                            continue
                    data_points.append(DataPoint(
                        timestamp=datetime.utcnow(),
                        value=alarm.get("message", ""),
                        metric="alarm",
                        labels={"severity": alarm.get("severity", "info")}
                    ))

            if data_points:
                return QueryResult(
                    success=True,
                    data=data_points,
                    query_type="metrics_data"
                )

            return None

        except Exception as e:
            logger.error(f"Error querying metrics data: {e}")
            return None

    async def _execute_promql(self, query_info: Dict[str, Any]) -> Optional[QueryResult]:
        """Execute a PromQL query against VictoriaMetrics."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                start = time.time()
                response = await client.get(
                    f"{self.victoria_metrics_url}/api/v1/query",
                    params={"query": query_info["query"]}
                )
                execution_time = (time.time() - start) * 1000

                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("data", {}).get("result", [])

                    data_points = []
                    for item in result_data:
                        value = item.get("value", [None, 0])
                        data_points.append(DataPoint(
                            timestamp=datetime.utcnow(),
                            value=float(value[1]) if len(value) > 1 else 0,
                            metric=query_info.get("metric", "unknown"),
                            labels=item.get("metric", {})
                        ))

                    return QueryResult(
                        success=True,
                        data=data_points,
                        raw_query=query_info["query"],
                        query_type="promql",
                        execution_time_ms=execution_time
                    )
        except Exception as e:
            logger.error(f"Error executing PromQL: {e}")

        return None

    def _build_response(
        self,
        query: str,
        intent: QueryIntent,
        entities: ExtractedEntities,
        query_results: List[QueryResult],
        language: str,
        metrics_data: Optional[Dict[str, Any]] = None
    ) -> NLPResponse:
        """Build the final response with answer and visualizations."""
        return self.response_builder.build(
            query=query,
            intent=intent,
            entities=entities,
            query_results=query_results,
            language=language,
            metrics_data=metrics_data
        )

    def _get_context(self, session_id: Optional[str]) -> Optional[ConversationContext]:
        """Get or create conversation context."""
        if not session_id:
            return None

        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id=session_id)

        return self.contexts[session_id]

    def _update_context(
        self,
        context: Optional[ConversationContext],
        query: str,
        intent: QueryIntent,
        entities: ExtractedEntities,
        results: List[QueryResult]
    ):
        """Update conversation context after processing."""
        if not context:
            return

        context.history.append({"role": "user", "content": query})
        context.last_intent = intent
        context.last_entities = entities
        context.last_results = results[0] if results else None

        # Update equipment context
        if entities.equipment:
            context.equipment_context = entities.equipment

        # Update time context
        if entities.time_range:
            context.time_context = entities.time_range

        context.updated_at = datetime.utcnow()

        # Limit history size
        if len(context.history) > 20:
            context.history = context.history[-20:]

    def _get_cache_key(self, query: ConversationalQuery) -> str:
        """Generate cache key for query."""
        key_str = f"{query.query}:{query.language}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_error_message(self, error: str, language: str) -> str:
        """Get localized error message."""
        if language == "fr":
            return f"Désolé, je n'ai pas pu traiter votre demande. Erreur: {error}"
        return f"Sorry, I couldn't process your request. Error: {error}"

    def clear_cache(self):
        """Clear query cache."""
        self.query_cache.clear()

    def clear_context(self, session_id: str):
        """Clear specific session context."""
        if session_id in self.contexts:
            del self.contexts[session_id]
