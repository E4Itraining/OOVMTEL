"""
Response Templates Module.

Provides enriched response templates for the SYNAPSIX AI assistant,
with structured formatting, visualizations, and contextual elements.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime


class TemplateType(str, Enum):
    """Types of response templates."""
    METRICS_SUMMARY = "metrics_summary"
    EQUIPMENT_STATUS = "equipment_status"
    ALERT_REPORT = "alert_report"
    OEE_ANALYSIS = "oee_analysis"
    TROUBLESHOOTING = "troubleshooting"
    MAINTENANCE = "maintenance"
    COMPARISON = "comparison"
    TREND = "trend"
    PRODUCTION = "production"
    ERROR = "error"
    GREETING = "greeting"
    CLARIFICATION = "clarification"


class StatusIndicator(str, Enum):
    """Visual status indicators."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    INFO = "info"
    UNKNOWN = "unknown"


@dataclass
class TemplateSection:
    """A section within a response template."""
    title: str
    content: str
    icon: Optional[str] = None
    collapsible: bool = False
    priority: int = 0


@dataclass
class ActionItem:
    """An actionable item in the response."""
    action: str
    priority: str  # high, medium, low
    equipment: Optional[str] = None
    deadline: Optional[str] = None


@dataclass
class MetricCard:
    """A metric display card."""
    name: str
    value: Any
    unit: str
    status: StatusIndicator = StatusIndicator.OK
    trend: Optional[str] = None  # up, down, stable
    threshold: Optional[float] = None
    change: Optional[float] = None
    change_period: Optional[str] = None


class ResponseTemplates:
    """
    Collection of response templates for structured output.

    Provides consistent, well-formatted responses across different
    query types and contexts.
    """

    # ==========================================================================
    # STATUS INDICATORS AND EMOJIS
    # ==========================================================================

    STATUS_EMOJI = {
        StatusIndicator.OK: "✅",
        StatusIndicator.WARNING: "⚠️",
        StatusIndicator.CRITICAL: "🔴",
        StatusIndicator.INFO: "ℹ️",
        StatusIndicator.UNKNOWN: "❓"
    }

    TREND_EMOJI = {
        "up": "📈",
        "down": "📉",
        "stable": "➡️"
    }

    PRIORITY_EMOJI = {
        "critical": "🚨",
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    # ==========================================================================
    # TEMPLATE METHODS - FRENCH
    # ==========================================================================

    @classmethod
    def format_metrics_summary(
        cls,
        metrics: List[MetricCard],
        title: str = "Résumé des Métriques",
        language: str = "fr"
    ) -> str:
        """Format a metrics summary response."""
        lines = [f"## {title}\n"]

        for metric in metrics:
            status_emoji = cls.STATUS_EMOJI.get(metric.status, "")
            trend_emoji = cls.TREND_EMOJI.get(metric.trend, "") if metric.trend else ""

            line = f"{status_emoji} **{metric.name}**: {metric.value} {metric.unit}"

            if metric.change is not None:
                change_sign = "+" if metric.change > 0 else ""
                line += f" ({change_sign}{metric.change:.1f}%)"

            if trend_emoji:
                line += f" {trend_emoji}"

            lines.append(line)

            if metric.threshold and metric.status == StatusIndicator.WARNING:
                if language == "fr":
                    lines.append(f"  └─ Seuil d'alerte: {metric.threshold} {metric.unit}")
                else:
                    lines.append(f"  └─ Alert threshold: {metric.threshold} {metric.unit}")

        return "\n".join(lines)

    @classmethod
    def format_equipment_status(
        cls,
        equipment_id: str,
        status: str,
        metrics: Dict[str, Any],
        health_score: Optional[float] = None,
        alerts: Optional[List[Dict[str, str]]] = None,
        language: str = "fr"
    ) -> str:
        """Format equipment status response."""
        status_map = {
            "running": (StatusIndicator.OK, "En fonctionnement" if language == "fr" else "Running"),
            "warning": (StatusIndicator.WARNING, "Attention requise" if language == "fr" else "Attention required"),
            "stopped": (StatusIndicator.CRITICAL, "Arrêté" if language == "fr" else "Stopped"),
            "maintenance": (StatusIndicator.INFO, "En maintenance" if language == "fr" else "In maintenance")
        }

        indicator, status_text = status_map.get(status, (StatusIndicator.UNKNOWN, status))
        emoji = cls.STATUS_EMOJI.get(indicator, "")

        lines = [
            f"## {emoji} État de {equipment_id}",
            f"**Statut**: {status_text}"
        ]

        if health_score is not None:
            health_emoji = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🔴"
            lines.append(f"**Score de santé**: {health_emoji} {health_score:.0f}/100")

        if metrics:
            lines.append("\n### Métriques actuelles" if language == "fr" else "\n### Current Metrics")
            for name, value in metrics.items():
                if isinstance(value, float):
                    lines.append(f"- {name}: {value:.2f}")
                else:
                    lines.append(f"- {name}: {value}")

        if alerts:
            lines.append("\n### Alertes actives" if language == "fr" else "\n### Active Alerts")
            for alert in alerts[:5]:
                severity_emoji = cls.PRIORITY_EMOJI.get(alert.get("severity", "low"), "")
                lines.append(f"{severity_emoji} {alert.get('message', 'N/A')}")

        return "\n".join(lines)

    @classmethod
    def format_oee_analysis(
        cls,
        oee: float,
        availability: float,
        performance: float,
        quality: float,
        production_count: int,
        defects: int,
        language: str = "fr"
    ) -> str:
        """Format OEE analysis response."""
        # Determine limiting factor
        components = {
            "availability" if language == "en" else "disponibilité": availability,
            "performance": performance,
            "quality" if language == "en" else "qualité": quality
        }
        limiting_factor = min(components, key=components.get)
        limiting_value = components[limiting_factor]

        # OEE status
        oee_status = StatusIndicator.OK if oee >= 85 else StatusIndicator.WARNING if oee >= 65 else StatusIndicator.CRITICAL
        oee_emoji = cls.STATUS_EMOJI.get(oee_status, "")

        if language == "fr":
            lines = [
                f"## {oee_emoji} Analyse OEE/TRS",
                "",
                "### Indicateurs principaux",
                f"| Indicateur | Valeur | Statut |",
                f"|------------|--------|--------|",
                f"| **OEE Global** | {oee:.1f}% | {'✅ World Class' if oee >= 85 else '⚠️ À améliorer'} |",
                f"| Disponibilité | {availability:.1f}% | {'✅' if availability >= 90 else '⚠️'} |",
                f"| Performance | {performance:.1f}% | {'✅' if performance >= 95 else '⚠️'} |",
                f"| Qualité | {quality:.1f}% | {'✅' if quality >= 99 else '⚠️'} |",
                "",
                "### Production",
                f"- Pièces produites: **{production_count:,}**",
                f"- Défauts: **{defects}** ({(defects/production_count*100) if production_count > 0 else 0:.2f}%)",
                "",
                f"### 📊 Facteur limitant: **{limiting_factor.capitalize()}** ({limiting_value:.1f}%)",
                "",
                "### Recommandations",
            ]

            if limiting_factor == "disponibilité":
                lines.extend([
                    "1. Analyser les causes d'arrêts non planifiés",
                    "2. Optimiser les temps de changement de série (SMED)",
                    "3. Renforcer la maintenance préventive"
                ])
            elif limiting_factor == "performance":
                lines.extend([
                    "1. Identifier les micro-arrêts et ralentissements",
                    "2. Vérifier les cadences machines vs. nominales",
                    "3. Former les opérateurs aux meilleures pratiques"
                ])
            else:
                lines.extend([
                    "1. Analyser les causes de non-qualité (Pareto)",
                    "2. Renforcer les contrôles en cours de production",
                    "3. Calibrer les équipements de mesure"
                ])
        else:
            lines = [
                f"## {oee_emoji} OEE Analysis",
                "",
                "### Key Indicators",
                f"| Indicator | Value | Status |",
                f"|-----------|-------|--------|",
                f"| **Overall OEE** | {oee:.1f}% | {'✅ World Class' if oee >= 85 else '⚠️ Needs Improvement'} |",
                f"| Availability | {availability:.1f}% | {'✅' if availability >= 90 else '⚠️'} |",
                f"| Performance | {performance:.1f}% | {'✅' if performance >= 95 else '⚠️'} |",
                f"| Quality | {quality:.1f}% | {'✅' if quality >= 99 else '⚠️'} |",
                "",
                "### Production",
                f"- Units produced: **{production_count:,}**",
                f"- Defects: **{defects}** ({(defects/production_count*100) if production_count > 0 else 0:.2f}%)",
                "",
                f"### 📊 Limiting factor: **{limiting_factor.capitalize()}** ({limiting_value:.1f}%)"
            ]

        return "\n".join(lines)

    @classmethod
    def format_troubleshooting(
        cls,
        symptom: str,
        probable_causes: List[Dict[str, Any]],
        recommended_actions: List[str],
        related_equipment: Optional[List[str]] = None,
        language: str = "fr"
    ) -> str:
        """Format troubleshooting response."""
        if language == "fr":
            lines = [
                "## 🔧 Diagnostic",
                "",
                f"### Symptôme signalé",
                f"> {symptom}",
                "",
                "### Causes probables"
            ]

            for i, cause in enumerate(probable_causes[:5], 1):
                probability = cause.get("probability", "N/A")
                if isinstance(probability, float):
                    probability = f"{probability:.0%}"
                lines.append(f"{i}. **{cause.get('cause', 'N/A')}** (probabilité: {probability})")
                if cause.get("explanation"):
                    lines.append(f"   └─ {cause['explanation']}")

            lines.extend([
                "",
                "### Actions recommandées"
            ])

            for i, action in enumerate(recommended_actions, 1):
                lines.append(f"{i}. {action}")

            if related_equipment:
                lines.extend([
                    "",
                    "### Équipements concernés",
                    ", ".join(related_equipment)
                ])

            lines.extend([
                "",
                "---",
                "💡 *Consultez le manuel de maintenance pour les procédures détaillées.*"
            ])
        else:
            lines = [
                "## 🔧 Troubleshooting",
                "",
                f"### Reported Symptom",
                f"> {symptom}",
                "",
                "### Probable Causes"
            ]

            for i, cause in enumerate(probable_causes[:5], 1):
                probability = cause.get("probability", "N/A")
                if isinstance(probability, float):
                    probability = f"{probability:.0%}"
                lines.append(f"{i}. **{cause.get('cause', 'N/A')}** (probability: {probability})")

            lines.extend([
                "",
                "### Recommended Actions"
            ])

            for i, action in enumerate(recommended_actions, 1):
                lines.append(f"{i}. {action}")

        return "\n".join(lines)

    @classmethod
    def format_alert_report(
        cls,
        alerts: List[Dict[str, Any]],
        summary: Optional[Dict[str, int]] = None,
        language: str = "fr"
    ) -> str:
        """Format alert report response."""
        if language == "fr":
            lines = ["## 🚨 Rapport d'Alertes"]

            if summary:
                lines.extend([
                    "",
                    "### Résumé",
                    f"- 🔴 Critiques: **{summary.get('critical', 0)}**",
                    f"- ⚠️ Avertissements: **{summary.get('warning', 0)}**",
                    f"- ℹ️ Informations: **{summary.get('info', 0)}**"
                ])

            if alerts:
                lines.extend(["", "### Alertes actives"])

                for alert in alerts[:10]:
                    severity = alert.get("severity", "info")
                    emoji = cls.PRIORITY_EMOJI.get(severity, "")
                    equipment = alert.get("equipment", "N/A")
                    message = alert.get("message", "N/A")
                    time = alert.get("timestamp", "")

                    lines.append(f"{emoji} **[{severity.upper()}]** {message}")
                    lines.append(f"   └─ Équipement: {equipment} | {time}")
            else:
                lines.extend(["", "✅ Aucune alerte active"])
        else:
            lines = ["## 🚨 Alert Report"]

            if summary:
                lines.extend([
                    "",
                    "### Summary",
                    f"- 🔴 Critical: **{summary.get('critical', 0)}**",
                    f"- ⚠️ Warnings: **{summary.get('warning', 0)}**",
                    f"- ℹ️ Info: **{summary.get('info', 0)}**"
                ])

            if alerts:
                lines.extend(["", "### Active Alerts"])

                for alert in alerts[:10]:
                    severity = alert.get("severity", "info")
                    emoji = cls.PRIORITY_EMOJI.get(severity, "")
                    lines.append(f"{emoji} **[{severity.upper()}]** {alert.get('message', 'N/A')}")
            else:
                lines.extend(["", "✅ No active alerts"])

        return "\n".join(lines)

    @classmethod
    def format_comparison(
        cls,
        title: str,
        items: List[Dict[str, Any]],
        metric_name: str,
        language: str = "fr"
    ) -> str:
        """Format comparison response."""
        if not items:
            return "Aucune donnée disponible pour la comparaison." if language == "fr" else "No data available for comparison."

        # Sort by value
        sorted_items = sorted(items, key=lambda x: x.get("value", 0), reverse=True)

        if language == "fr":
            lines = [
                f"## 📊 Comparaison: {title}",
                "",
                f"### Classement par {metric_name}",
                ""
            ]

            for i, item in enumerate(sorted_items, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                name = item.get("name", "N/A")
                value = item.get("value", 0)
                unit = item.get("unit", "")

                lines.append(f"{medal} **{name}**: {value:.1f} {unit}")

            # Add insights
            best = sorted_items[0]
            worst = sorted_items[-1]
            diff = best.get("value", 0) - worst.get("value", 0)

            lines.extend([
                "",
                "### Insights",
                f"- Écart max: **{diff:.1f}** entre {best.get('name')} et {worst.get('name')}",
            ])
        else:
            lines = [
                f"## 📊 Comparison: {title}",
                "",
                f"### Ranking by {metric_name}",
                ""
            ]

            for i, item in enumerate(sorted_items, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                lines.append(f"{medal} **{item.get('name', 'N/A')}**: {item.get('value', 0):.1f} {item.get('unit', '')}")

        return "\n".join(lines)

    @classmethod
    def format_maintenance_recommendation(
        cls,
        equipment_id: str,
        health_score: float,
        rul_days: Optional[int],
        recommendations: List[Dict[str, Any]],
        language: str = "fr"
    ) -> str:
        """Format maintenance recommendation response."""
        health_emoji = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🔴"

        if language == "fr":
            lines = [
                f"## 🔧 Recommandations de Maintenance",
                f"### {equipment_id}",
                "",
                f"**Score de santé**: {health_emoji} {health_score:.0f}/100"
            ]

            if rul_days is not None:
                rul_status = "✅" if rul_days > 30 else "⚠️" if rul_days > 7 else "🔴"
                lines.append(f"**Durée de vie résiduelle**: {rul_status} {rul_days} jours")

            lines.extend(["", "### Actions recommandées"])

            for rec in recommendations:
                priority = rec.get("priority", "medium")
                emoji = cls.PRIORITY_EMOJI.get(priority, "")
                lines.append(f"{emoji} **[{priority.upper()}]** {rec.get('action', 'N/A')}")
                if rec.get("reason"):
                    lines.append(f"   └─ Raison: {rec['reason']}")
                if rec.get("deadline"):
                    lines.append(f"   └─ Échéance: {rec['deadline']}")
        else:
            lines = [
                f"## 🔧 Maintenance Recommendations",
                f"### {equipment_id}",
                "",
                f"**Health Score**: {health_emoji} {health_score:.0f}/100"
            ]

            if rul_days is not None:
                lines.append(f"**Remaining Useful Life**: {rul_days} days")

            lines.extend(["", "### Recommended Actions"])

            for rec in recommendations:
                priority = rec.get("priority", "medium")
                emoji = cls.PRIORITY_EMOJI.get(priority, "")
                lines.append(f"{emoji} **[{priority.upper()}]** {rec.get('action', 'N/A')}")

        return "\n".join(lines)

    @classmethod
    def format_greeting(
        cls,
        user_name: Optional[str] = None,
        active_alerts: int = 0,
        oee_today: Optional[float] = None,
        language: str = "fr"
    ) -> str:
        """Format greeting/welcome response."""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Bonjour" if language == "fr" else "Good morning"
        elif hour < 18:
            greeting = "Bon après-midi" if language == "fr" else "Good afternoon"
        else:
            greeting = "Bonsoir" if language == "fr" else "Good evening"

        if user_name:
            greeting += f", {user_name}"

        if language == "fr":
            lines = [
                f"## 👋 {greeting}!",
                "",
                "Je suis **SYNAPSIX**, votre assistant d'observabilité industrielle.",
                "",
                "### État actuel"
            ]

            if active_alerts > 0:
                lines.append(f"- 🚨 **{active_alerts}** alerte(s) active(s)")
            else:
                lines.append("- ✅ Aucune alerte critique")

            if oee_today is not None:
                oee_emoji = "✅" if oee_today >= 85 else "⚠️" if oee_today >= 65 else "🔴"
                lines.append(f"- {oee_emoji} OEE du jour: **{oee_today:.1f}%**")

            lines.extend([
                "",
                "### Comment puis-je vous aider?",
                "- 📊 Consulter les métriques de production",
                "- 🔧 Diagnostiquer un problème d'équipement",
                "- 📈 Analyser les tendances",
                "- 🚨 Vérifier les alertes actives"
            ])
        else:
            lines = [
                f"## 👋 {greeting}!",
                "",
                "I'm **SYNAPSIX**, your industrial observability assistant.",
                "",
                "### Current Status"
            ]

            if active_alerts > 0:
                lines.append(f"- 🚨 **{active_alerts}** active alert(s)")
            else:
                lines.append("- ✅ No critical alerts")

            if oee_today is not None:
                oee_emoji = "✅" if oee_today >= 85 else "⚠️"
                lines.append(f"- {oee_emoji} Today's OEE: **{oee_today:.1f}%**")

            lines.extend([
                "",
                "### How can I help you?",
                "- 📊 Check production metrics",
                "- 🔧 Diagnose equipment issues",
                "- 📈 Analyze trends",
                "- 🚨 Review active alerts"
            ])

        return "\n".join(lines)

    @classmethod
    def format_clarification(
        cls,
        question: str,
        options: List[str],
        context: Optional[str] = None,
        language: str = "fr"
    ) -> str:
        """Format clarification request."""
        if language == "fr":
            lines = [
                "## ❓ Clarification nécessaire",
                "",
                f"**{question}**"
            ]

            if context:
                lines.extend(["", f"Contexte: _{context}_"])

            if options:
                lines.extend(["", "Options possibles:"])
                for i, option in enumerate(options, 1):
                    lines.append(f"{i}. {option}")
        else:
            lines = [
                "## ❓ Clarification needed",
                "",
                f"**{question}**"
            ]

            if options:
                lines.extend(["", "Possible options:"])
                for i, option in enumerate(options, 1):
                    lines.append(f"{i}. {option}")

        return "\n".join(lines)

    @classmethod
    def format_error(
        cls,
        error_message: str,
        suggestions: Optional[List[str]] = None,
        language: str = "fr"
    ) -> str:
        """Format error response."""
        if language == "fr":
            lines = [
                "## ⚠️ Problème rencontré",
                "",
                f"_{error_message}_"
            ]

            if suggestions:
                lines.extend(["", "### Suggestions:"])
                for suggestion in suggestions:
                    lines.append(f"- {suggestion}")
        else:
            lines = [
                "## ⚠️ Issue encountered",
                "",
                f"_{error_message}_"
            ]

            if suggestions:
                lines.extend(["", "### Suggestions:"])
                for suggestion in suggestions:
                    lines.append(f"- {suggestion}")

        return "\n".join(lines)


class ResponseFormatter:
    """
    Utility class for formatting and enhancing responses.
    """

    @staticmethod
    def add_follow_up_suggestions(
        response: str,
        suggestions: List[str],
        language: str = "fr"
    ) -> str:
        """Add follow-up question suggestions to response."""
        if not suggestions:
            return response

        header = "\n\n---\n### 💡 " + ("Questions suggérées" if language == "fr" else "Suggested questions") + "\n"
        suggestion_lines = [f"- {s}" for s in suggestions[:3]]

        return response + header + "\n".join(suggestion_lines)

    @staticmethod
    def add_data_source(
        response: str,
        source: str,
        timestamp: Optional[datetime] = None,
        language: str = "fr"
    ) -> str:
        """Add data source attribution to response."""
        if timestamp is None:
            timestamp = datetime.utcnow()

        time_str = timestamp.strftime("%H:%M:%S")

        if language == "fr":
            footer = f"\n\n---\n_Source: {source} | Mis à jour: {time_str}_"
        else:
            footer = f"\n\n---\n_Source: {source} | Updated: {time_str}_"

        return response + footer

    @staticmethod
    def convert_to_html(markdown: str) -> str:
        """Convert markdown response to HTML (basic conversion)."""
        import re

        html = markdown

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'

        return html
