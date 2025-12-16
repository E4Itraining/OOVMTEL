"""
Query Generator - Generates PromQL and OpenSearch queries from extracted entities
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .models import QueryIntent, ExtractedEntities, TimeRange


class QueryGenerator:
    """
    Generates database queries from natural language entities.

    Supports:
    - PromQL for VictoriaMetrics
    - OpenSearch query DSL for logs
    """

    # Metric name mappings to actual metric names in the system
    METRIC_MAPPINGS = {
        "oee": "mes_oee_percent",
        "quality_rate": "mes_quality_rate_percent",
        "availability": "mes_availability_percent",
        "performance": "mes_performance_percent",
        "production_count": "mes_production_count_total",
        "defects": "mes_defects_total",
        "cycle_time": "mes_cycle_time_seconds",
        "temperature": "scada_temperature_celsius",
        "pressure": "scada_pressure_bar",
        "vibration": "scada_vibration_mm_s",
        "power_consumption": "scada_power_consumption_kw",
        "flow_rate": "scada_flow_rate_m3_h",
        "downtime": "mes_downtime_seconds_total",
        "failures": "scada_failures_total",
    }

    # Equipment type to label mappings
    EQUIPMENT_LABELS = {
        "line": "production_line",
        "reactor": "equipment_type",
        "pump": "equipment_type",
        "mixer": "equipment_type",
        "furnace": "equipment_type",
        "conveyor": "equipment_type",
        "tank": "equipment_type",
        "sensor": "sensor_type",
    }

    def __init__(
        self,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
        opensearch_url: str = "http://opensearch:9200"
    ):
        self.victoria_metrics_url = victoria_metrics_url
        self.opensearch_url = opensearch_url

    def generate_promql(
        self,
        intent: QueryIntent,
        entities: ExtractedEntities
    ) -> List[Dict[str, Any]]:
        """
        Generate PromQL queries based on intent and entities.

        Returns list of query info dicts with:
        - query: The PromQL query string
        - metric: The metric name
        - description: Human-readable description
        """
        queries = []

        # Get time range for queries
        time_range = entities.time_range or TimeRange.last_hours(24)
        duration = self._get_duration_string(time_range)

        # Determine which metrics to query
        metrics_to_query = entities.metrics if entities.metrics else self._default_metrics_for_intent(intent)

        for metric in metrics_to_query:
            metric_name = self.METRIC_MAPPINGS.get(metric, metric)

            # Build label filters
            label_filters = self._build_label_filters(entities)

            # Generate appropriate query based on intent
            if intent == QueryIntent.METRICS_QUERY:
                query = self._generate_instant_query(metric_name, label_filters)
            elif intent == QueryIntent.TREND_ANALYSIS:
                query = self._generate_range_query(metric_name, label_filters, duration)
            elif intent == QueryIntent.COMPARISON:
                query = self._generate_comparison_query(metric_name, entities, duration)
            elif intent == QueryIntent.ALERT_STATUS:
                query = self._generate_alert_query(label_filters)
            elif intent == QueryIntent.SUMMARY:
                query = self._generate_summary_query(metric_name, label_filters, duration)
            else:
                query = self._generate_instant_query(metric_name, label_filters)

            queries.append({
                "query": query,
                "metric": metric,
                "metric_name": metric_name,
                "description": f"Query for {metric}",
                "time_range": duration
            })

        return queries

    def generate_opensearch_query(
        self,
        intent: QueryIntent,
        entities: ExtractedEntities
    ) -> Dict[str, Any]:
        """Generate OpenSearch query DSL for log searches."""
        time_range = entities.time_range or TimeRange.last_hours(24)

        # Build base query
        must_clauses = []

        # Add time range filter
        must_clauses.append({
            "range": {
                "@timestamp": {
                    "gte": time_range.start.isoformat(),
                    "lte": time_range.end.isoformat()
                }
            }
        })

        # Add equipment filters
        if entities.equipment:
            must_clauses.append({
                "terms": {
                    "equipment.keyword": entities.equipment
                }
            })

        # Add severity filters for alerts
        if entities.severity_levels:
            must_clauses.append({
                "terms": {
                    "severity.keyword": entities.severity_levels
                }
            })

        # Add intent-specific filters
        if intent == QueryIntent.TROUBLESHOOTING:
            must_clauses.append({
                "terms": {
                    "level.keyword": ["error", "critical", "warning"]
                }
            })
        elif intent == QueryIntent.ALERT_STATUS:
            must_clauses.append({
                "exists": {"field": "alert_name"}
            })

        return {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "sort": [{"@timestamp": "desc"}],
            "size": 100
        }

    def _generate_instant_query(
        self,
        metric_name: str,
        label_filters: str
    ) -> str:
        """Generate query for current value."""
        if label_filters:
            return f"{metric_name}{{{label_filters}}}"
        return metric_name

    def _generate_range_query(
        self,
        metric_name: str,
        label_filters: str,
        duration: str
    ) -> str:
        """Generate query for time range."""
        base = f"{metric_name}{{{label_filters}}}" if label_filters else metric_name
        return f"avg_over_time({base}[{duration}])"

    def _generate_comparison_query(
        self,
        metric_name: str,
        entities: ExtractedEntities,
        duration: str
    ) -> str:
        """Generate query for comparing equipment/lines."""
        if entities.equipment:
            # Group by equipment
            label_filters = self._build_label_filters(entities)
            base = f"{metric_name}{{{label_filters}}}" if label_filters else metric_name
            return f"avg by (equipment) ({base})"
        elif entities.production_lines:
            # Group by production line
            lines_pattern = "|".join(entities.production_lines)
            return f'avg by (production_line) ({metric_name}{{production_line=~"{lines_pattern}"}})'
        else:
            # Default: group by all labels
            return f"avg by (equipment) ({metric_name})"

    def _generate_alert_query(self, label_filters: str) -> str:
        """Generate query for active alerts."""
        if label_filters:
            return f'ALERTS{{{label_filters}}}'
        return "ALERTS"

    def _generate_summary_query(
        self,
        metric_name: str,
        label_filters: str,
        duration: str
    ) -> str:
        """Generate aggregated summary query."""
        base = f"{metric_name}{{{label_filters}}}" if label_filters else metric_name
        return f"avg({base})"

    def _build_label_filters(self, entities: ExtractedEntities) -> str:
        """Build PromQL label filter string."""
        filters = []

        # Equipment filters
        if entities.equipment:
            equipment_regex = "|".join(entities.equipment)
            filters.append(f'equipment=~"{equipment_regex}"')

        # Equipment type filters
        if entities.equipment_types:
            for eq_type in entities.equipment_types:
                label_name = self.EQUIPMENT_LABELS.get(eq_type, "equipment_type")
                filters.append(f'{label_name}="{eq_type}"')

        # Production line filters
        if entities.production_lines:
            line_regex = "|".join(entities.production_lines)
            filters.append(f'production_line=~"{line_regex}"')

        return ", ".join(filters)

    def _default_metrics_for_intent(self, intent: QueryIntent) -> List[str]:
        """Get default metrics to query based on intent."""
        if intent == QueryIntent.PRODUCTION_STATUS:
            return ["oee", "production_count", "quality_rate"]
        elif intent == QueryIntent.EQUIPMENT_STATUS:
            return ["temperature", "pressure", "vibration"]
        elif intent == QueryIntent.SUMMARY:
            return ["oee", "quality_rate", "availability", "performance"]
        elif intent == QueryIntent.TROUBLESHOOTING:
            return ["failures", "downtime", "defects"]
        elif intent == QueryIntent.ALERT_STATUS:
            return []  # Alerts have their own query
        else:
            return ["oee"]

    def _get_duration_string(self, time_range: TimeRange) -> str:
        """Convert TimeRange to PromQL duration string."""
        delta = time_range.end - time_range.start
        total_hours = delta.total_seconds() / 3600

        if total_hours <= 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes}m"
        elif total_hours <= 24:
            return f"{int(total_hours)}h"
        else:
            days = int(total_hours / 24)
            return f"{days}d"
