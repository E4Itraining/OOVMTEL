"""
Causal Graph Builder - Constructs causal graphs for root cause analysis
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

from .models import (
    Incident,
    CausalNode,
    CausalEdge,
    CausalGraph,
    CorrelationResult,
    NodeType,
    CAUSAL_KNOWLEDGE_BASE,
)


class CausalGraphBuilder:
    """
    Builds causal graphs from incidents, events, and correlations.

    The graph represents:
    - Nodes: Incidents, symptoms, causes, metrics, events
    - Edges: Causal relationships with strength scores
    """

    def __init__(self):
        self.knowledge_base = CAUSAL_KNOWLEDGE_BASE

    def build_graph(
        self,
        incident: Incident,
        events: List[Dict],
        metrics: Dict[str, List],
        alerts: List[Dict],
        correlations: List[CorrelationResult]
    ) -> CausalGraph:
        """
        Build a causal graph for the given incident.

        Args:
            incident: The incident being analyzed
            events: Related events
            metrics: Related metric time series
            alerts: Related alerts
            correlations: Correlation analysis results

        Returns:
            CausalGraph with nodes and edges
        """
        graph = CausalGraph(incident_id=incident.id)

        # 1. Add incident node (this is the effect we're explaining)
        incident_node = CausalNode(
            id=f"node-{incident.id}",
            type=NodeType.INCIDENT,
            name=incident.title,
            description=incident.description,
            timestamp=incident.detected_at,
            probability=1.0,  # The incident definitely happened
            confidence=1.0
        )
        graph.nodes.append(incident_node)

        # 2. Add symptom nodes from affected metrics
        symptom_nodes = self._create_symptom_nodes(incident, metrics)
        graph.nodes.extend(symptom_nodes)

        # Link symptoms to incident
        for symptom in symptom_nodes:
            graph.edges.append(CausalEdge(
                source_id=symptom.id,
                target_id=incident_node.id,
                relationship="symptom_of",
                strength=0.8,
                evidence="Metric anomaly detected during incident"
            ))

        # 3. Add event nodes
        event_nodes = self._create_event_nodes(events, incident.detected_at)
        graph.nodes.extend(event_nodes)

        # 4. Add alert nodes
        alert_nodes = self._create_alert_nodes(alerts, incident.detected_at)
        graph.nodes.extend(alert_nodes)

        # Link alerts to symptoms or incident
        for alert_node in alert_nodes:
            # Find related symptom
            related_symptom = self._find_related_node(alert_node, symptom_nodes)
            if related_symptom:
                graph.edges.append(CausalEdge(
                    source_id=alert_node.id,
                    target_id=related_symptom.id,
                    relationship="indicates",
                    strength=0.9,
                    evidence="Alert triggered for this metric"
                ))
            else:
                graph.edges.append(CausalEdge(
                    source_id=alert_node.id,
                    target_id=incident_node.id,
                    relationship="indicates",
                    strength=0.7
                ))

        # 5. Add cause nodes from knowledge base
        cause_nodes = self._create_cause_nodes(symptom_nodes, event_nodes)
        graph.nodes.extend(cause_nodes)

        # Link causes to symptoms
        for cause_node in cause_nodes:
            related_symptoms = self._find_effects_for_cause(cause_node, symptom_nodes)
            for symptom in related_symptoms:
                graph.edges.append(CausalEdge(
                    source_id=cause_node.id,
                    target_id=symptom.id,
                    relationship="causes",
                    strength=0.6,
                    evidence=f"Known causal relationship from knowledge base"
                ))

        # 6. Add correlation-based edges
        self._add_correlation_edges(graph, correlations)

        # 7. Calculate node probabilities based on graph structure
        self._calculate_probabilities(graph)

        return graph

    def _create_symptom_nodes(
        self,
        incident: Incident,
        metrics: Dict[str, List]
    ) -> List[CausalNode]:
        """Create symptom nodes from metrics."""
        nodes = []

        for metric_name, values in metrics.items():
            if not values:
                continue

            # Calculate baseline and current
            numeric_values = [v.get("value", 0) for v in values]
            if not numeric_values:
                continue

            current_value = numeric_values[0]  # Most recent
            baseline = sum(numeric_values) / len(numeric_values)

            # Calculate deviation
            deviation_pct = 0
            if baseline != 0:
                deviation_pct = ((current_value - baseline) / baseline) * 100

            # Only create node if significant deviation
            if abs(deviation_pct) > 5:
                direction = "elevated" if deviation_pct > 0 else "reduced"
                nodes.append(CausalNode(
                    id=f"symptom-{uuid.uuid4().hex[:8]}",
                    type=NodeType.SYMPTOM,
                    name=f"{direction.capitalize()} {metric_name.replace('_', ' ')}",
                    description=f"{metric_name} is {direction} by {abs(deviation_pct):.1f}%",
                    timestamp=values[0].get("timestamp") if values else None,
                    metric_value=current_value,
                    metric_baseline=baseline,
                    deviation_percent=deviation_pct,
                    metadata={"metric": metric_name}
                ))

        return nodes

    def _create_event_nodes(
        self,
        events: List[Dict],
        incident_time: datetime
    ) -> List[CausalNode]:
        """Create nodes from events."""
        nodes = []

        for event in events:
            event_time = event.get("timestamp")
            if isinstance(event_time, str):
                try:
                    event_time = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
                except ValueError:
                    event_time = incident_time - timedelta(minutes=5)

            # Only include events that happened before/around the incident
            if event_time and (incident_time - event_time).total_seconds() < 3600:
                equipment = event.get("equipment", "System")
                status = event.get("status", "unknown")

                nodes.append(CausalNode(
                    id=f"event-{uuid.uuid4().hex[:8]}",
                    type=NodeType.EVENT,
                    name=f"{equipment} {status}",
                    description=f"Equipment {equipment} status: {status}",
                    timestamp=event_time,
                    equipment=equipment,
                    metadata=event
                ))

        return nodes

    def _create_alert_nodes(
        self,
        alerts: List[Dict],
        incident_time: datetime
    ) -> List[CausalNode]:
        """Create nodes from alerts."""
        nodes = []

        for alert in alerts:
            alert_time = alert.get("timestamp")
            if isinstance(alert_time, str):
                try:
                    alert_time = datetime.fromisoformat(alert_time.replace("Z", "+00:00"))
                except ValueError:
                    alert_time = incident_time - timedelta(minutes=2)

            severity = alert.get("severity", "info")
            message = alert.get("message", "Alert")

            nodes.append(CausalNode(
                id=f"alert-{uuid.uuid4().hex[:8]}",
                type=NodeType.ALERT,
                name=f"[{severity.upper()}] {message[:50]}",
                description=message,
                timestamp=alert_time,
                metadata={"severity": severity}
            ))

        return nodes

    def _create_cause_nodes(
        self,
        symptom_nodes: List[CausalNode],
        event_nodes: List[CausalNode]
    ) -> List[CausalNode]:
        """Create potential cause nodes from knowledge base."""
        cause_nodes = []
        added_causes = set()

        # For each symptom, find potential causes
        for symptom in symptom_nodes:
            symptom_name = symptom.name.lower()

            for pattern_name, pattern_info in self.knowledge_base.items():
                pattern_display = pattern_name.replace("_", " ")

                # Check if this pattern matches the symptom
                if pattern_display in symptom_name or any(
                    effect.replace("_", " ") in symptom_name
                    for effect in pattern_info.get("effects", [])
                ):
                    # Add cause nodes for this pattern
                    for cause in pattern_info.get("causes", []):
                        cause_key = cause.lower()
                        if cause_key not in added_causes:
                            added_causes.add(cause_key)

                            cause_nodes.append(CausalNode(
                                id=f"cause-{uuid.uuid4().hex[:8]}",
                                type=NodeType.CAUSE,
                                name=cause.replace("_", " ").title(),
                                description=f"Potential cause: {cause.replace('_', ' ')}",
                                timestamp=symptom.timestamp - timedelta(minutes=10) if symptom.timestamp else None,
                                metadata={
                                    "source_pattern": pattern_name,
                                    "category": pattern_info.get("category")
                                }
                            ))

        # Also check events for causes
        for event in event_nodes:
            event_type = event.name.lower()

            if "warning" in event_type or "error" in event_type:
                equipment = event.equipment or "Unknown"
                cause_key = f"issue_{equipment}".lower()

                if cause_key not in added_causes:
                    added_causes.add(cause_key)
                    cause_nodes.append(CausalNode(
                        id=f"cause-{uuid.uuid4().hex[:8]}",
                        type=NodeType.CAUSE,
                        name=f"Issue with {equipment}",
                        description=f"Equipment {equipment} reported warning/error",
                        timestamp=event.timestamp,
                        equipment=equipment
                    ))

        return cause_nodes

    def _find_related_node(
        self,
        source_node: CausalNode,
        target_nodes: List[CausalNode]
    ) -> Optional[CausalNode]:
        """Find a related node based on name/content similarity."""
        source_words = set(source_node.name.lower().split())

        best_match = None
        best_score = 0

        for target in target_nodes:
            target_words = set(target.name.lower().split())
            overlap = len(source_words & target_words)

            if overlap > best_score:
                best_score = overlap
                best_match = target

        return best_match if best_score > 0 else None

    def _find_effects_for_cause(
        self,
        cause_node: CausalNode,
        symptom_nodes: List[CausalNode]
    ) -> List[CausalNode]:
        """Find symptoms that could be effects of this cause."""
        related = []
        cause_name = cause_node.name.lower()

        # Look up in knowledge base
        for pattern_name, pattern_info in self.knowledge_base.items():
            if pattern_name.replace("_", " ") in cause_name:
                effects = pattern_info.get("effects", [])

                for symptom in symptom_nodes:
                    symptom_name = symptom.name.lower()
                    for effect in effects:
                        if effect.replace("_", " ") in symptom_name:
                            related.append(symptom)
                            break

        # Also use simple keyword matching
        if not related:
            cause_words = set(cause_name.split())
            for symptom in symptom_nodes:
                symptom_words = set(symptom.name.lower().split())
                if cause_words & symptom_words:
                    related.append(symptom)

        return related

    def _add_correlation_edges(
        self,
        graph: CausalGraph,
        correlations: List[CorrelationResult]
    ):
        """Add edges based on correlation analysis."""
        # Build index of nodes by metric name
        metric_to_node = {}
        for node in graph.nodes:
            if node.metadata.get("metric"):
                metric_to_node[node.metadata["metric"]] = node

        for corr in correlations:
            if not corr.is_significant:
                continue

            # Find nodes for these metrics
            node_a = metric_to_node.get(corr.metric_a)
            node_b = metric_to_node.get(corr.metric_b)

            if node_a and node_b:
                # Direction: if lag > 0, A precedes B, so A might cause B
                if corr.lag_seconds > 0:
                    source, target = node_a, node_b
                else:
                    source, target = node_b, node_a

                # Check if edge already exists
                existing = [e for e in graph.edges
                           if e.source_id == source.id and e.target_id == target.id]

                if not existing:
                    graph.edges.append(CausalEdge(
                        source_id=source.id,
                        target_id=target.id,
                        relationship="correlates_with",
                        strength=abs(corr.correlation),
                        lag_seconds=abs(corr.lag_seconds),
                        evidence=f"Correlation: {corr.correlation:.2f}, lag: {corr.lag_seconds}s"
                    ))

    def _calculate_probabilities(self, graph: CausalGraph):
        """Calculate probability scores for all nodes."""
        # Nodes with no incoming edges (potential root causes) get higher base probability
        incoming_counts = defaultdict(int)
        outgoing_counts = defaultdict(int)

        for edge in graph.edges:
            incoming_counts[edge.target_id] += 1
            outgoing_counts[edge.source_id] += 1

        for node in graph.nodes:
            if node.type == NodeType.INCIDENT:
                continue  # Incident probability stays at 1.0

            # Base probability
            prob = 0.3

            # More outgoing edges = more likely to be a cause
            out_count = outgoing_counts.get(node.id, 0)
            prob += min(out_count * 0.1, 0.3)

            # Fewer incoming edges = more likely to be root cause
            in_count = incoming_counts.get(node.id, 0)
            if in_count == 0:
                prob += 0.2

            # Deviation magnitude
            if node.deviation_percent:
                prob += min(abs(node.deviation_percent) * 0.005, 0.2)

            # Temporal proximity to incident
            incident_node = next(
                (n for n in graph.nodes if n.type == NodeType.INCIDENT),
                None
            )
            if incident_node and node.timestamp and incident_node.timestamp:
                time_diff = abs((incident_node.timestamp - node.timestamp).total_seconds())
                if time_diff < 300:  # Within 5 minutes
                    prob += 0.1

            node.probability = min(prob, 1.0)
            node.confidence = 0.5 + (out_count * 0.1)  # More evidence = more confidence

        # Identify likely root causes (high outgoing, no incoming)
        for node in graph.nodes:
            if node.type == NodeType.CAUSE:
                in_count = incoming_counts.get(node.id, 0)
                out_count = outgoing_counts.get(node.id, 0)

                if in_count == 0 and out_count > 0:
                    node.type = NodeType.ROOT_CAUSE
                    if node.id not in graph.root_causes:
                        graph.root_causes.append(node.id)
