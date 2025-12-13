"""
RCA Engine - Main root cause analysis engine
Automatically identifies root causes of industrial incidents
"""

import time
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .models import (
    Incident,
    IncidentSeverity,
    IncidentCategory,
    CausalNode,
    CausalEdge,
    CausalGraph,
    RootCauseResult,
    RCAAnalysis,
    CorrelationResult,
    RemediationSuggestion,
    NodeType,
    CAUSAL_KNOWLEDGE_BASE,
    HISTORICAL_PATTERNS,
)
from .correlator import TemporalCorrelator
from .graph_builder import CausalGraphBuilder

logger = logging.getLogger(__name__)


class RCAEngine:
    """
    Automatic Root Cause Analysis Engine.

    Features:
    - Incident detection from metrics/alerts
    - Temporal correlation analysis
    - Causal graph construction
    - Root cause probability scoring
    - Historical pattern matching
    - Remediation suggestions
    """

    def __init__(
        self,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
        opensearch_url: str = "http://opensearch:9200",
        lookback_minutes: int = 60,
        correlation_threshold: float = 0.7,
    ):
        self.victoria_metrics_url = victoria_metrics_url
        self.opensearch_url = opensearch_url
        self.lookback_minutes = lookback_minutes
        self.correlation_threshold = correlation_threshold

        self.correlator = TemporalCorrelator(correlation_threshold)
        self.graph_builder = CausalGraphBuilder()

        # Cache for recent analyses
        self.analysis_cache: Dict[str, RCAAnalysis] = {}

        logger.info("RCA Engine initialized")

    async def analyze_incident(
        self,
        incident: Incident,
        metrics_data: Optional[Dict[str, Any]] = None,
        include_historical: bool = True
    ) -> RCAAnalysis:
        """
        Perform root cause analysis on an incident.

        Args:
            incident: The incident to analyze
            metrics_data: Optional pre-fetched metrics data
            include_historical: Whether to include historical pattern matching

        Returns:
            Complete RCA analysis with causal graph and root causes
        """
        start_time = time.time()

        try:
            # 1. Gather relevant data
            events, metrics, alerts = await self._gather_context(incident, metrics_data)

            # 2. Perform temporal correlation analysis
            correlations = self.correlator.analyze_correlations(metrics, events)

            # 3. Build causal graph
            causal_graph = self.graph_builder.build_graph(
                incident=incident,
                events=events,
                metrics=metrics,
                alerts=alerts,
                correlations=correlations
            )

            # 4. Calculate root cause probabilities
            root_causes = self._calculate_root_cause_probabilities(
                causal_graph, correlations, incident
            )

            # 5. Match historical patterns
            if include_historical:
                root_causes = self._enhance_with_historical(root_causes, events, metrics)

            # 6. Generate remediation suggestions
            for rc in root_causes:
                rc.remediation = self._get_remediation_suggestion(rc)

            # 7. Build timeline
            timeline = self._build_timeline(events, alerts, incident)

            # 8. Generate summary
            summary, summary_html = self._generate_summary(incident, root_causes, timeline)

            analysis = RCAAnalysis(
                incident=incident,
                causal_graph=causal_graph,
                root_causes=root_causes,
                correlations=correlations,
                timeline=timeline,
                analysis_duration_ms=(time.time() - start_time) * 1000,
                summary=summary,
                summary_html=summary_html
            )

            # Cache the analysis
            self.analysis_cache[incident.id] = analysis

            return analysis

        except Exception as e:
            logger.error(f"Error in RCA analysis: {e}")
            raise

    async def detect_incidents(
        self,
        metrics_data: Dict[str, Any],
        thresholds: Optional[Dict[str, float]] = None
    ) -> List[Incident]:
        """
        Automatically detect incidents from current metrics.

        Args:
            metrics_data: Current metrics data
            thresholds: Optional custom thresholds

        Returns:
            List of detected incidents
        """
        incidents = []
        default_thresholds = {
            "oee_min": 75.0,
            "quality_rate_min": 95.0,
            "cpu_max": 90.0,
            "memory_max": 85.0,
            "temperature_max": 80.0,
            "vibration_max": 10.0,
        }
        thresholds = {**default_thresholds, **(thresholds or {})}

        business = metrics_data.get("business", {})
        tech = metrics_data.get("tech", {})

        # Check OEE
        oee = business.get("oee", 100)
        if oee < thresholds["oee_min"]:
            incidents.append(Incident(
                id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                title=f"OEE Drop Detected ({oee:.1f}%)",
                description=f"OEE has dropped below {thresholds['oee_min']}% threshold",
                severity=IncidentSeverity.HIGH if oee < 70 else IncidentSeverity.MEDIUM,
                category=IncidentCategory.PERFORMANCE,
                detected_at=datetime.utcnow(),
                metrics_affected=["oee", "availability", "performance", "quality"],
                impact_description=f"Production efficiency at {oee:.1f}%"
            ))

        # Check quality rate
        quality_rate = business.get("quality_rate", 100)
        if quality_rate < thresholds["quality_rate_min"]:
            incidents.append(Incident(
                id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                title=f"Quality Rate Drop ({quality_rate:.1f}%)",
                description=f"Quality rate below {thresholds['quality_rate_min']}% threshold",
                severity=IncidentSeverity.HIGH,
                category=IncidentCategory.QUALITY,
                detected_at=datetime.utcnow(),
                metrics_affected=["quality_rate", "defects"],
                impact_description=f"Quality at {quality_rate:.1f}%, defects: {business.get('defects_today', 0)}"
            ))

        # Check CPU
        cpu = tech.get("cpu_usage", 0)
        if cpu > thresholds["cpu_max"]:
            incidents.append(Incident(
                id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                title=f"High CPU Usage ({cpu:.1f}%)",
                description=f"CPU usage exceeds {thresholds['cpu_max']}% threshold",
                severity=IncidentSeverity.HIGH if cpu > 95 else IncidentSeverity.MEDIUM,
                category=IncidentCategory.INFRASTRUCTURE,
                detected_at=datetime.utcnow(),
                metrics_affected=["cpu_usage", "latency"],
                impact_description=f"System CPU at {cpu:.1f}%"
            ))

        # Check equipment alarms
        alarms = business.get("alarms", [])
        for alarm in alarms:
            if alarm.get("severity") == "critical":
                incidents.append(Incident(
                    id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                    title=f"Critical Alarm: {alarm.get('message', 'Unknown')}",
                    description=alarm.get("message", "Critical alarm detected"),
                    severity=IncidentSeverity.CRITICAL,
                    category=IncidentCategory.EQUIPMENT,
                    detected_at=datetime.utcnow(),
                    metrics_affected=["alarms"],
                    tags=["alarm", "critical"]
                ))

        # Check equipment status
        equipment = business.get("equipment", [])
        for eq in equipment:
            if eq.get("status") == "warning":
                temp = eq.get("temp", 0)
                if temp > thresholds.get("temperature_max", 80):
                    incidents.append(Incident(
                        id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                        title=f"High Temperature on {eq.get('name')}",
                        description=f"Temperature {temp:.1f}°C exceeds threshold",
                        severity=IncidentSeverity.MEDIUM,
                        category=IncidentCategory.EQUIPMENT,
                        detected_at=datetime.utcnow(),
                        equipment=eq.get("name"),
                        metrics_affected=["temperature"],
                        impact_description=f"Equipment temperature at {temp:.1f}°C"
                    ))

        return incidents

    async def _gather_context(
        self,
        incident: Incident,
        metrics_data: Optional[Dict[str, Any]]
    ) -> Tuple[List[Dict], Dict[str, List], List[Dict]]:
        """Gather events, metrics, and alerts related to the incident."""
        events = []
        metrics = {}
        alerts = []

        # Use provided metrics data if available
        if metrics_data:
            business = metrics_data.get("business", {})
            tech = metrics_data.get("tech", {})

            # Extract equipment events
            for eq in business.get("equipment", []):
                events.append({
                    "timestamp": incident.detected_at - timedelta(minutes=5),
                    "type": "equipment_status",
                    "equipment": eq.get("name"),
                    "status": eq.get("status"),
                    "temperature": eq.get("temp"),
                    "pressure": eq.get("pressure"),
                    "power": eq.get("power"),
                })

            # Extract metrics as time series (simulated recent values)
            now = datetime.utcnow()
            for metric in ["oee", "quality_rate", "availability", "performance"]:
                if metric in business:
                    # Simulate degradation over last hour
                    values = []
                    base_value = business[metric]
                    for i in range(12):  # 12 x 5 min = 1 hour
                        t = now - timedelta(minutes=i * 5)
                        # Simulate gradual degradation
                        degradation = (12 - i) * 0.5 if i < 6 else 0
                        values.append({
                            "timestamp": t,
                            "value": min(100, base_value + degradation)
                        })
                    metrics[metric] = values

            # Add tech metrics
            for metric in ["cpu_usage", "memory_usage"]:
                if metric in tech:
                    values = []
                    base_value = tech[metric]
                    for i in range(12):
                        t = now - timedelta(minutes=i * 5)
                        # Simulate increase leading to incident
                        increase = (12 - i) * 2 if i < 6 else 0
                        values.append({
                            "timestamp": t,
                            "value": max(0, base_value - increase)
                        })
                    metrics[metric] = values

            # Extract alerts
            for alarm in business.get("alarms", []):
                alerts.append({
                    "timestamp": incident.detected_at - timedelta(minutes=2),
                    "severity": alarm.get("severity"),
                    "message": alarm.get("message"),
                    "type": "alarm"
                })

        return events, metrics, alerts

    def _calculate_root_cause_probabilities(
        self,
        graph: CausalGraph,
        correlations: List[CorrelationResult],
        incident: Incident
    ) -> List[RootCauseResult]:
        """Calculate probability scores for potential root causes."""
        root_cause_results = []

        for node in graph.nodes:
            if node.type in [NodeType.CAUSE, NodeType.ROOT_CAUSE]:
                # Calculate probability based on multiple factors
                probability = 0.0
                confidence = 0.0
                evidence = []

                # Factor 1: Temporal precedence (causes should precede effects)
                if node.timestamp and node.timestamp < incident.detected_at:
                    time_diff = (incident.detected_at - node.timestamp).total_seconds()
                    if time_diff < 300:  # Within 5 minutes
                        probability += 0.3
                        evidence.append(f"Occurred {time_diff:.0f}s before incident")

                # Factor 2: Correlation strength
                related_correlations = [
                    c for c in correlations
                    if node.name.lower() in c.metric_a.lower() or node.name.lower() in c.metric_b.lower()
                ]
                if related_correlations:
                    max_corr = max(c.correlation for c in related_correlations)
                    probability += max_corr * 0.25
                    evidence.append(f"Correlation strength: {max_corr:.2f}")

                # Factor 3: Deviation from baseline
                if node.deviation_percent:
                    dev = abs(node.deviation_percent)
                    if dev > 20:
                        probability += 0.25
                        evidence.append(f"Deviation: {dev:.1f}% from baseline")
                    elif dev > 10:
                        probability += 0.15
                        evidence.append(f"Deviation: {dev:.1f}% from baseline")

                # Factor 4: Knowledge base matching
                kb_match = self._match_knowledge_base(node.name, incident)
                if kb_match:
                    probability += 0.2
                    evidence.append(f"Matches known pattern: {kb_match}")

                # Factor 5: Graph centrality (nodes with more edges are more suspicious)
                edge_count = len([e for e in graph.edges if e.source_id == node.id])
                if edge_count > 2:
                    probability += 0.1
                    evidence.append(f"Connected to {edge_count} other factors")

                # Normalize probability
                probability = min(probability, 1.0)

                # Calculate confidence based on evidence count
                confidence = min(len(evidence) * 0.2, 1.0)

                if probability > 0.3:  # Only include if somewhat likely
                    root_cause_results.append(RootCauseResult(
                        node=node,
                        probability=probability,
                        confidence=confidence,
                        evidence=evidence,
                        contributing_factors=[
                            n.name for n in graph.get_children(node.id)
                        ]
                    ))

        # Sort by probability
        root_cause_results.sort(key=lambda x: x.probability, reverse=True)

        # Mark top result as root cause in graph
        if root_cause_results:
            top_rc = root_cause_results[0]
            if top_rc.node.id not in graph.root_causes:
                graph.root_causes.append(top_rc.node.id)
                top_rc.node.type = NodeType.ROOT_CAUSE

        return root_cause_results

    def _match_knowledge_base(self, node_name: str, incident: Incident) -> Optional[str]:
        """Match node against knowledge base."""
        node_lower = node_name.lower()

        for pattern_name, pattern_info in CAUSAL_KNOWLEDGE_BASE.items():
            if pattern_name.replace("_", " ") in node_lower:
                # Check if any effects match incident category
                for effect in pattern_info.get("effects", []):
                    if incident.category.value in effect or effect in incident.title.lower():
                        return pattern_name
        return None

    def _enhance_with_historical(
        self,
        root_causes: List[RootCauseResult],
        events: List[Dict],
        metrics: Dict[str, List]
    ) -> List[RootCauseResult]:
        """Enhance root cause probabilities with historical patterns."""
        # Extract current signature
        current_signature = set()
        for event in events:
            if event.get("status") == "warning":
                current_signature.add("equipment_warning")
            if event.get("temperature", 0) > 70:
                current_signature.add("high_temperature")

        for metric_name, values in metrics.items():
            if values:
                current_value = values[0].get("value", 0)
                if "temperature" in metric_name and current_value > 70:
                    current_signature.add("high_temperature")
                if "cpu" in metric_name and current_value > 80:
                    current_signature.add("high_cpu")
                if "vibration" in metric_name and current_value > 8:
                    current_signature.add("high_vibration")
                if "oee" in metric_name and current_value < 75:
                    current_signature.add("oee_drop")

        # Match against historical patterns
        for pattern in HISTORICAL_PATTERNS:
            pattern_signature = set(pattern["signature"])
            overlap = current_signature & pattern_signature

            if len(overlap) >= len(pattern_signature) * 0.5:
                # Found matching pattern, boost related root causes
                for rc in root_causes:
                    if pattern["root_cause"].replace("_", " ") in rc.node.name.lower():
                        rc.probability = min(rc.probability + 0.2, 1.0)
                        rc.evidence.append(
                            f"Matches historical pattern {pattern['pattern_id']} "
                            f"({pattern['occurrences']} occurrences, "
                            f"{pattern['success_rate']*100:.0f}% success rate)"
                        )

        return root_causes

    def _get_remediation_suggestion(self, root_cause: RootCauseResult) -> RemediationSuggestion:
        """Get remediation suggestion for a root cause."""
        node_name_lower = root_cause.node.name.lower()

        # Common remediations
        remediations = {
            "temperature": RemediationSuggestion(
                id=f"REM-{uuid.uuid4().hex[:8].upper()}",
                title="Check Cooling System",
                description="Verify cooling system operation and clean filters",
                priority=1,
                category="inspection",
                estimated_time_minutes=30,
                requires_downtime=False,
                auto_executable=False,
                steps=[
                    "Check cooling system status",
                    "Inspect and clean air filters",
                    "Verify coolant levels",
                    "Check fan operation",
                    "Monitor temperature after intervention"
                ],
                historical_success_rate=0.85
            ),
            "vibration": RemediationSuggestion(
                id=f"REM-{uuid.uuid4().hex[:8].upper()}",
                title="Inspect Mechanical Components",
                description="Check bearings, alignment, and balance",
                priority=1,
                category="maintenance",
                estimated_time_minutes=60,
                requires_downtime=True,
                auto_executable=False,
                steps=[
                    "Stop equipment safely",
                    "Inspect bearings for wear",
                    "Check shaft alignment",
                    "Verify mounting bolts torque",
                    "Check for imbalance",
                    "Replace worn components",
                    "Test after maintenance"
                ],
                historical_success_rate=0.92
            ),
            "cpu": RemediationSuggestion(
                id=f"REM-{uuid.uuid4().hex[:8].upper()}",
                title="Restart Service",
                description="Restart the affected service to clear memory",
                priority=1,
                category="restart",
                estimated_time_minutes=5,
                requires_downtime=True,
                auto_executable=True,
                runbook_id="RB-RESTART-001",
                steps=[
                    "Identify affected service",
                    "Notify stakeholders",
                    "Gracefully stop service",
                    "Clear temporary files",
                    "Restart service",
                    "Verify service health"
                ],
                historical_success_rate=0.95
            ),
            "memory": RemediationSuggestion(
                id=f"REM-{uuid.uuid4().hex[:8].upper()}",
                title="Memory Optimization",
                description="Clear caches and restart if needed",
                priority=1,
                category="restart",
                estimated_time_minutes=10,
                requires_downtime=False,
                auto_executable=True,
                runbook_id="RB-MEMORY-001",
                steps=[
                    "Clear application caches",
                    "Force garbage collection",
                    "If issue persists, restart service",
                    "Monitor memory usage"
                ],
                historical_success_rate=0.90
            ),
            "quality": RemediationSuggestion(
                id=f"REM-{uuid.uuid4().hex[:8].upper()}",
                title="Quality Investigation",
                description="Investigate quality issues and recalibrate",
                priority=1,
                category="inspection",
                estimated_time_minutes=45,
                requires_downtime=False,
                auto_executable=False,
                steps=[
                    "Review recent quality data",
                    "Inspect material batch",
                    "Check process parameters",
                    "Verify sensor calibration",
                    "Adjust settings if needed",
                    "Run test batch"
                ],
                historical_success_rate=0.88
            ),
            "oee": RemediationSuggestion(
                id=f"REM-{uuid.uuid4().hex[:8].upper()}",
                title="OEE Recovery Plan",
                description="Comprehensive review of availability, performance, and quality",
                priority=1,
                category="analysis",
                estimated_time_minutes=60,
                requires_downtime=False,
                auto_executable=False,
                steps=[
                    "Analyze availability losses (downtime)",
                    "Analyze performance losses (speed)",
                    "Analyze quality losses (defects)",
                    "Identify top loss category",
                    "Implement targeted improvements",
                    "Monitor OEE recovery"
                ],
                historical_success_rate=0.80
            ),
        }

        # Find matching remediation
        for keyword, remediation in remediations.items():
            if keyword in node_name_lower:
                return remediation

        # Default remediation
        return RemediationSuggestion(
            id=f"REM-{uuid.uuid4().hex[:8].upper()}",
            title="Investigate Issue",
            description="Manual investigation required",
            priority=2,
            category="investigation",
            estimated_time_minutes=30,
            requires_downtime=False,
            auto_executable=False,
            steps=[
                "Review related metrics and logs",
                "Check equipment status",
                "Consult with subject matter expert",
                "Document findings"
            ],
            historical_success_rate=0.70
        )

    def _build_timeline(
        self,
        events: List[Dict],
        alerts: List[Dict],
        incident: Incident
    ) -> List[Dict[str, Any]]:
        """Build chronological timeline of events leading to incident."""
        timeline = []

        # Add events
        for event in events:
            timeline.append({
                "timestamp": event.get("timestamp", datetime.utcnow()).isoformat(),
                "type": "event",
                "category": event.get("type", "unknown"),
                "description": f"{event.get('equipment', 'System')}: {event.get('status', 'update')}",
                "details": event
            })

        # Add alerts
        for alert in alerts:
            timeline.append({
                "timestamp": alert.get("timestamp", datetime.utcnow()).isoformat(),
                "type": "alert",
                "category": alert.get("severity", "info"),
                "description": alert.get("message", "Alert triggered"),
                "details": alert
            })

        # Add incident detection
        timeline.append({
            "timestamp": incident.detected_at.isoformat(),
            "type": "incident",
            "category": incident.severity.value,
            "description": f"Incident detected: {incident.title}",
            "details": {"incident_id": incident.id}
        })

        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])

        return timeline

    def _generate_summary(
        self,
        incident: Incident,
        root_causes: List[RootCauseResult],
        timeline: List[Dict]
    ) -> Tuple[str, str]:
        """Generate human-readable summary of RCA."""
        lines = []
        lines.append(f"## Analyse de l'incident: {incident.title}\n")
        lines.append(f"**Sévérité**: {incident.severity.value.upper()}")
        lines.append(f"**Catégorie**: {incident.category.value}")
        lines.append(f"**Détecté à**: {incident.detected_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

        if root_causes:
            lines.append("### Cause Racine Identifiée\n")
            primary = root_causes[0]
            lines.append(f"🎯 **{primary.node.name}** (Probabilité: {primary.probability*100:.0f}%)\n")

            if primary.evidence:
                lines.append("**Éléments de preuve:**")
                for evidence in primary.evidence:
                    lines.append(f"- {evidence}")

            if primary.remediation:
                lines.append(f"\n### Action Recommandée\n")
                lines.append(f"**{primary.remediation.title}**")
                lines.append(f"{primary.remediation.description}")
                lines.append(f"- Temps estimé: {primary.remediation.estimated_time_minutes} min")
                lines.append(f"- Taux de succès historique: {primary.remediation.historical_success_rate*100:.0f}%")

            if len(root_causes) > 1:
                lines.append("\n### Causes Alternatives\n")
                for rc in root_causes[1:3]:
                    lines.append(f"- {rc.node.name} ({rc.probability*100:.0f}%)")
        else:
            lines.append("\n⚠️ Aucune cause racine identifiée avec certitude.")
            lines.append("Une investigation manuelle est recommandée.")

        summary = "\n".join(lines)

        # Convert to HTML
        summary_html = summary.replace("\n", "<br>")
        summary_html = summary_html.replace("## ", "<h2>").replace("### ", "<h3>")
        summary_html = summary_html.replace("**", "<strong>", 1)
        while "**" in summary_html:
            summary_html = summary_html.replace("**", "</strong>", 1)
            if "**" in summary_html:
                summary_html = summary_html.replace("**", "<strong>", 1)

        return summary, summary_html

    def get_cached_analysis(self, incident_id: str) -> Optional[RCAAnalysis]:
        """Get cached analysis by incident ID."""
        return self.analysis_cache.get(incident_id)

    def clear_cache(self):
        """Clear analysis cache."""
        self.analysis_cache.clear()
