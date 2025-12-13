"""
Response Builder - Builds natural language responses with visualizations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import (
    QueryIntent,
    ExtractedEntities,
    QueryResult,
    NLPResponse,
    SuggestedVisualization,
    VisualizationType,
    DataPoint,
)


class ResponseBuilder:
    """
    Builds user-friendly responses from query results.

    Features:
    - Natural language answer generation
    - Visualization suggestions
    - Follow-up question suggestions
    - Multi-language support (FR/EN)
    """

    # Response templates by intent and language
    TEMPLATES = {
        "fr": {
            QueryIntent.METRICS_QUERY: {
                "single": "La valeur actuelle de {metric} est de {value}{unit}.",
                "multiple": "Voici les valeurs actuelles :\n{metrics_list}",
                "no_data": "Aucune donnée disponible pour {metric}.",
            },
            QueryIntent.SUMMARY: {
                "intro": "Voici un résumé de la situation :\n\n",
                "oee": "**OEE** : {value:.1f}% {status}",
                "quality": "**Qualité** : {value:.1f}%",
                "availability": "**Disponibilité** : {value:.1f}%",
                "performance": "**Performance** : {value:.1f}%",
                "production": "**Production** : {value} unités",
                "defects": "**Défauts** : {value}",
                "alarms": "**Alarmes critiques** : {value}",
            },
            QueryIntent.EQUIPMENT_STATUS: {
                "intro": "État des équipements :\n\n",
                "running": "✅ **{name}** : En marche (T={temp:.1f}°C)",
                "warning": "⚠️ **{name}** : Attention requise (T={temp:.1f}°C)",
                "stopped": "⛔ **{name}** : Arrêté",
                "unknown": "❓ **{name}** : État inconnu",
            },
            QueryIntent.ALERT_STATUS: {
                "intro": "Alertes actives :\n\n",
                "critical": "🔴 **CRITIQUE** : {message}",
                "warning": "🟡 **ATTENTION** : {message}",
                "info": "🔵 **INFO** : {message}",
                "no_alerts": "✅ Aucune alerte active.",
            },
            QueryIntent.TROUBLESHOOTING: {
                "intro": "Analyse du problème :\n\n",
                "found": "J'ai identifié {count} événement(s) potentiellement lié(s) :\n{events}",
                "suggestion": "\n💡 **Suggestion** : {suggestion}",
                "no_issues": "Aucun problème détecté dans la période analysée.",
            },
            QueryIntent.COMPARISON: {
                "intro": "Comparaison :\n\n",
                "row": "• **{name}** : {value}{unit}",
                "best": "\n🏆 Meilleur : {name} ({value}{unit})",
                "worst": "\n⚠️ À améliorer : {name} ({value}{unit})",
            },
            QueryIntent.TREND_ANALYSIS: {
                "intro": "Analyse des tendances sur {period} :\n\n",
                "increasing": "📈 **{metric}** : En hausse ({change:+.1f}%)",
                "decreasing": "📉 **{metric}** : En baisse ({change:+.1f}%)",
                "stable": "➡️ **{metric}** : Stable",
            },
            QueryIntent.PREDICTION: {
                "intro": "Prédiction pour {metric} :\n\n",
                "result": "Valeur estimée dans {horizon} : {value}{unit}",
                "confidence": "Confiance : {confidence:.0f}%",
            },
        },
        "en": {
            QueryIntent.METRICS_QUERY: {
                "single": "The current value of {metric} is {value}{unit}.",
                "multiple": "Here are the current values:\n{metrics_list}",
                "no_data": "No data available for {metric}.",
            },
            QueryIntent.SUMMARY: {
                "intro": "Here's a summary of the current situation:\n\n",
                "oee": "**OEE**: {value:.1f}% {status}",
                "quality": "**Quality**: {value:.1f}%",
                "availability": "**Availability**: {value:.1f}%",
                "performance": "**Performance**: {value:.1f}%",
                "production": "**Production**: {value} units",
                "defects": "**Defects**: {value}",
                "alarms": "**Critical alarms**: {value}",
            },
            QueryIntent.EQUIPMENT_STATUS: {
                "intro": "Equipment status:\n\n",
                "running": "✅ **{name}**: Running (T={temp:.1f}°C)",
                "warning": "⚠️ **{name}**: Attention needed (T={temp:.1f}°C)",
                "stopped": "⛔ **{name}**: Stopped",
                "unknown": "❓ **{name}**: Unknown state",
            },
            QueryIntent.ALERT_STATUS: {
                "intro": "Active alerts:\n\n",
                "critical": "🔴 **CRITICAL**: {message}",
                "warning": "🟡 **WARNING**: {message}",
                "info": "🔵 **INFO**: {message}",
                "no_alerts": "✅ No active alerts.",
            },
            QueryIntent.TROUBLESHOOTING: {
                "intro": "Problem analysis:\n\n",
                "found": "I found {count} potentially related event(s):\n{events}",
                "suggestion": "\n💡 **Suggestion**: {suggestion}",
                "no_issues": "No issues detected in the analyzed period.",
            },
            QueryIntent.COMPARISON: {
                "intro": "Comparison:\n\n",
                "row": "• **{name}**: {value}{unit}",
                "best": "\n🏆 Best: {name} ({value}{unit})",
                "worst": "\n⚠️ Needs improvement: {name} ({value}{unit})",
            },
            QueryIntent.TREND_ANALYSIS: {
                "intro": "Trend analysis over {period}:\n\n",
                "increasing": "📈 **{metric}**: Increasing ({change:+.1f}%)",
                "decreasing": "📉 **{metric}**: Decreasing ({change:+.1f}%)",
                "stable": "➡️ **{metric}**: Stable",
            },
            QueryIntent.PREDICTION: {
                "intro": "Prediction for {metric}:\n\n",
                "result": "Estimated value in {horizon}: {value}{unit}",
                "confidence": "Confidence: {confidence:.0f}%",
            },
        }
    }

    # Metric units
    UNITS = {
        "oee": "%",
        "quality_rate": "%",
        "availability": "%",
        "performance": "%",
        "production_count": " units",
        "defects": "",
        "cycle_time": "s",
        "temperature": "°C",
        "pressure": " bar",
        "vibration": " mm/s",
        "power_consumption": " kW",
        "flow_rate": " m³/h",
    }

    # Follow-up suggestions by intent
    SUGGESTIONS = {
        "fr": {
            QueryIntent.SUMMARY: [
                "Montre-moi les tendances sur la semaine",
                "Quels équipements ont des alertes ?",
                "Compare les performances des lignes",
            ],
            QueryIntent.EQUIPMENT_STATUS: [
                "Pourquoi cet équipement est en warning ?",
                "Historique des pannes sur cet équipement",
                "Quand est prévue la prochaine maintenance ?",
            ],
            QueryIntent.ALERT_STATUS: [
                "Quelle est la cause de cette alerte ?",
                "Historique des alertes similaires",
                "Quelles actions correctives sont recommandées ?",
            ],
            QueryIntent.TROUBLESHOOTING: [
                "Quelle est la cause racine probable ?",
                "Y a-t-il eu des incidents similaires ?",
                "Quelles actions correctives recommandes-tu ?",
            ],
            QueryIntent.METRICS_QUERY: [
                "Montre l'évolution sur 24h",
                "Compare avec hier",
                "Y a-t-il des anomalies ?",
            ],
        },
        "en": {
            QueryIntent.SUMMARY: [
                "Show me trends for the week",
                "Which equipment has alerts?",
                "Compare line performances",
            ],
            QueryIntent.EQUIPMENT_STATUS: [
                "Why is this equipment in warning state?",
                "Failure history for this equipment",
                "When is the next maintenance scheduled?",
            ],
            QueryIntent.ALERT_STATUS: [
                "What's causing this alert?",
                "History of similar alerts",
                "What corrective actions are recommended?",
            ],
            QueryIntent.TROUBLESHOOTING: [
                "What's the likely root cause?",
                "Have there been similar incidents?",
                "What corrective actions do you recommend?",
            ],
            QueryIntent.METRICS_QUERY: [
                "Show evolution over 24h",
                "Compare with yesterday",
                "Are there any anomalies?",
            ],
        }
    }

    def build(
        self,
        query: str,
        intent: QueryIntent,
        entities: ExtractedEntities,
        query_results: List[QueryResult],
        language: str,
        metrics_data: Optional[Dict[str, Any]] = None
    ) -> NLPResponse:
        """Build complete response from query results."""

        templates = self.TEMPLATES.get(language, self.TEMPLATES["en"])
        intent_templates = templates.get(intent, templates[QueryIntent.METRICS_QUERY])

        # Build answer based on intent
        if intent == QueryIntent.SUMMARY:
            answer, visualizations = self._build_summary_response(
                intent_templates, metrics_data, language
            )
        elif intent == QueryIntent.EQUIPMENT_STATUS:
            answer, visualizations = self._build_equipment_response(
                intent_templates, query_results, metrics_data, language
            )
        elif intent == QueryIntent.ALERT_STATUS:
            answer, visualizations = self._build_alert_response(
                intent_templates, query_results, metrics_data, language
            )
        elif intent == QueryIntent.COMPARISON:
            answer, visualizations = self._build_comparison_response(
                intent_templates, query_results, entities, language
            )
        elif intent == QueryIntent.TROUBLESHOOTING:
            answer, visualizations = self._build_troubleshooting_response(
                intent_templates, query_results, entities, metrics_data, language
            )
        else:
            answer, visualizations = self._build_metrics_response(
                intent_templates, query_results, entities, language
            )

        # Get follow-up suggestions
        suggestions = self._get_suggestions(intent, language)

        # Calculate confidence
        confidence = self._calculate_confidence(query_results, entities)

        return NLPResponse(
            answer=answer,
            answer_html=self._to_html(answer),
            intent=intent,
            entities=entities,
            query_results=query_results,
            visualizations=visualizations,
            suggestions=suggestions,
            confidence=confidence,
            language=language
        )

    def _build_summary_response(
        self,
        templates: Dict[str, str],
        metrics_data: Optional[Dict[str, Any]],
        language: str
    ) -> tuple[str, List[SuggestedVisualization]]:
        """Build summary response."""
        if not metrics_data:
            return "No data available.", []

        business = metrics_data.get("business", {})
        lines = [templates["intro"]]

        # OEE with status indicator
        oee = business.get("oee", 0)
        status = "🟢" if oee >= 85 else "🟡" if oee >= 75 else "🔴"
        lines.append(templates["oee"].format(value=oee, status=status))

        # Other KPIs
        if "quality_rate" in business:
            lines.append(templates["quality"].format(value=business["quality_rate"]))
        if "availability" in business:
            lines.append(templates["availability"].format(value=business["availability"]))
        if "performance" in business:
            lines.append(templates["performance"].format(value=business["performance"]))
        if "production_today" in business:
            lines.append(templates["production"].format(value=business["production_today"]))
        if "defects_today" in business:
            lines.append(templates["defects"].format(value=business["defects_today"]))
        if "critical_alarms" in business:
            lines.append(templates["alarms"].format(value=business["critical_alarms"]))

        # Build visualization
        visualizations = [
            SuggestedVisualization(
                type=VisualizationType.GAUGE,
                title="OEE",
                config={"min": 0, "max": 100, "thresholds": [75, 85]},
                data=[{"value": oee}],
                description="Overall Equipment Effectiveness"
            ),
            SuggestedVisualization(
                type=VisualizationType.BAR_CHART,
                title="KPI Overview" if language == "en" else "Vue d'ensemble KPIs",
                data=[
                    {"name": "OEE", "value": oee},
                    {"name": "Quality" if language == "en" else "Qualité", "value": business.get("quality_rate", 0)},
                    {"name": "Availability" if language == "en" else "Disponibilité", "value": business.get("availability", 0)},
                    {"name": "Performance", "value": business.get("performance", 0)},
                ]
            )
        ]

        return "\n".join(lines), visualizations

    def _build_equipment_response(
        self,
        templates: Dict[str, str],
        query_results: List[QueryResult],
        metrics_data: Optional[Dict[str, Any]],
        language: str
    ) -> tuple[str, List[SuggestedVisualization]]:
        """Build equipment status response."""
        lines = [templates["intro"]]
        equipment_data = []

        if metrics_data and "business" in metrics_data:
            equipment_list = metrics_data["business"].get("equipment", [])
            for eq in equipment_list:
                name = eq.get("name", "Unknown")
                status = eq.get("status", "unknown")
                temp = eq.get("temp", 0)

                template_key = status if status in templates else "unknown"
                lines.append(templates[template_key].format(name=name, temp=temp))

                equipment_data.append({
                    "name": name,
                    "status": status,
                    "temperature": temp,
                    "pressure": eq.get("pressure", 0),
                    "power": eq.get("power", 0)
                })

        visualizations = [
            SuggestedVisualization(
                type=VisualizationType.TABLE,
                title="Equipment Status" if language == "en" else "État des équipements",
                data=equipment_data,
                config={"columns": ["name", "status", "temperature", "pressure", "power"]}
            )
        ]

        return "\n".join(lines), visualizations

    def _build_alert_response(
        self,
        templates: Dict[str, str],
        query_results: List[QueryResult],
        metrics_data: Optional[Dict[str, Any]],
        language: str
    ) -> tuple[str, List[SuggestedVisualization]]:
        """Build alert status response."""
        lines = [templates["intro"]]
        alert_data = []

        if metrics_data and "business" in metrics_data:
            alarms = metrics_data["business"].get("alarms", [])

            if not alarms:
                lines.append(templates["no_alerts"])
            else:
                for alarm in alarms:
                    severity = alarm.get("severity", "info")
                    message = alarm.get("message", "")
                    template_key = severity if severity in templates else "info"
                    lines.append(templates[template_key].format(message=message))

                    alert_data.append({
                        "severity": severity,
                        "message": message
                    })

        visualizations = []
        if alert_data:
            visualizations.append(
                SuggestedVisualization(
                    type=VisualizationType.TABLE,
                    title="Active Alerts" if language == "en" else "Alertes actives",
                    data=alert_data,
                    config={"columns": ["severity", "message"]}
                )
            )

        return "\n".join(lines), visualizations

    def _build_comparison_response(
        self,
        templates: Dict[str, str],
        query_results: List[QueryResult],
        entities: ExtractedEntities,
        language: str
    ) -> tuple[str, List[SuggestedVisualization]]:
        """Build comparison response."""
        lines = [templates["intro"]]
        comparison_data = []

        for result in query_results:
            for dp in result.data:
                name = dp.labels.get("equipment", dp.labels.get("production_line", dp.metric))
                value = dp.value
                unit = self.UNITS.get(dp.metric, "")

                lines.append(templates["row"].format(name=name, value=value, unit=unit))
                comparison_data.append({"name": name, "value": value})

        if comparison_data:
            best = max(comparison_data, key=lambda x: x["value"])
            worst = min(comparison_data, key=lambda x: x["value"])
            unit = self.UNITS.get(entities.metrics[0] if entities.metrics else "", "")

            lines.append(templates["best"].format(name=best["name"], value=best["value"], unit=unit))
            lines.append(templates["worst"].format(name=worst["name"], value=worst["value"], unit=unit))

        visualizations = [
            SuggestedVisualization(
                type=VisualizationType.BAR_CHART,
                title="Comparison" if language == "en" else "Comparaison",
                data=comparison_data
            )
        ]

        return "\n".join(lines), visualizations

    def _build_troubleshooting_response(
        self,
        templates: Dict[str, str],
        query_results: List[QueryResult],
        entities: ExtractedEntities,
        metrics_data: Optional[Dict[str, Any]],
        language: str
    ) -> tuple[str, List[SuggestedVisualization]]:
        """Build troubleshooting response."""
        lines = [templates["intro"]]
        events = []

        # Gather events from results
        for result in query_results:
            for dp in result.data:
                events.append(f"• {dp.metric}: {dp.value}")

        # Add alerts as potential causes
        if metrics_data and "business" in metrics_data:
            alarms = metrics_data["business"].get("alarms", [])
            for alarm in alarms:
                events.append(f"• ⚠️ {alarm.get('message', '')}")

        if events:
            lines.append(templates["found"].format(
                count=len(events),
                events="\n".join(events[:5])  # Limit to 5
            ))

            # Add suggestion based on common patterns
            suggestion = self._get_troubleshooting_suggestion(events, language)
            if suggestion:
                lines.append(templates["suggestion"].format(suggestion=suggestion))
        else:
            lines.append(templates["no_issues"])

        visualizations = [
            SuggestedVisualization(
                type=VisualizationType.TIMELINE,
                title="Event Timeline" if language == "en" else "Chronologie des événements",
                data=[{"event": e} for e in events[:10]]
            )
        ]

        return "\n".join(lines), visualizations

    def _build_metrics_response(
        self,
        templates: Dict[str, str],
        query_results: List[QueryResult],
        entities: ExtractedEntities,
        language: str
    ) -> tuple[str, List[SuggestedVisualization]]:
        """Build generic metrics response."""
        if not query_results or not any(r.data for r in query_results):
            metric = entities.metrics[0] if entities.metrics else "requested metric"
            return templates["no_data"].format(metric=metric), []

        lines = []
        viz_data = []

        for result in query_results:
            for dp in result.data:
                metric = dp.metric
                value = dp.value
                unit = self.UNITS.get(metric, "")

                if isinstance(value, float):
                    lines.append(templates["single"].format(
                        metric=metric, value=f"{value:.2f}", unit=unit
                    ))
                else:
                    lines.append(templates["single"].format(
                        metric=metric, value=value, unit=unit
                    ))

                viz_data.append({"metric": metric, "value": value})

        visualizations = []
        if viz_data:
            visualizations.append(
                SuggestedVisualization(
                    type=VisualizationType.STAT_CARD,
                    title="Metrics" if language == "en" else "Métriques",
                    data=viz_data
                )
            )

        return "\n".join(lines) if lines else templates["no_data"].format(metric="metrics"), visualizations

    def _get_suggestions(self, intent: QueryIntent, language: str) -> List[str]:
        """Get follow-up suggestions."""
        suggestions = self.SUGGESTIONS.get(language, self.SUGGESTIONS["en"])
        return suggestions.get(intent, suggestions[QueryIntent.METRICS_QUERY])

    def _get_troubleshooting_suggestion(self, events: List[str], language: str) -> Optional[str]:
        """Get troubleshooting suggestion based on events."""
        events_text = " ".join(events).lower()

        suggestions = {
            "fr": {
                "temperature": "Vérifiez le système de refroidissement et les ventilateurs.",
                "vibration": "Inspectez les roulements et l'alignement de l'équipement.",
                "pressure": "Vérifiez les vannes et recherchez des fuites.",
                "cpu": "Redémarrez le service ou augmentez les ressources.",
                "memory": "Recherchez des fuites mémoire ou augmentez la RAM.",
            },
            "en": {
                "temperature": "Check cooling system and fans.",
                "vibration": "Inspect bearings and equipment alignment.",
                "pressure": "Check valves and look for leaks.",
                "cpu": "Restart service or increase resources.",
                "memory": "Look for memory leaks or increase RAM.",
            }
        }

        lang_suggestions = suggestions.get(language, suggestions["en"])
        for keyword, suggestion in lang_suggestions.items():
            if keyword in events_text:
                return suggestion

        return None

    def _calculate_confidence(
        self,
        query_results: List[QueryResult],
        entities: ExtractedEntities
    ) -> float:
        """Calculate confidence score for the response."""
        confidence = 0.5  # Base confidence

        # Increase confidence if we got data
        if query_results and any(r.success and r.data for r in query_results):
            confidence += 0.3

        # Increase confidence if entities were extracted
        if entities.metrics or entities.equipment:
            confidence += 0.1

        # Increase confidence if time range was specified
        if entities.time_range:
            confidence += 0.1

        return min(confidence, 1.0)

    def _to_html(self, markdown: str) -> str:
        """Convert markdown to simple HTML."""
        html = markdown
        # Bold
        html = html.replace("**", "<strong>", 1)
        while "**" in html:
            html = html.replace("**", "</strong>", 1)
            if "**" in html:
                html = html.replace("**", "<strong>", 1)
        # Line breaks
        html = html.replace("\n", "<br>")
        return html
