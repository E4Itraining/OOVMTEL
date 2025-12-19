"""
Impact Analyzer - Analyze downstream impact of data changes
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

from .models import (
    LineageNode,
    LineageGraph,
    ImpactAnalysis,
    DataProvenance,
    DataFlowPath,
    NodeType,
    DataQuality,
)
from .graph_manager import GraphManager

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Analyze impact of changes in data lineage.

    Features:
    - Downstream impact analysis
    - Risk assessment
    - Change recommendations
    - Data provenance tracking
    """

    def __init__(self, graph_manager: GraphManager):
        self._graph_manager = graph_manager

        # Risk weights by node type
        self._risk_weights = {
            NodeType.VISUALIZATION: 1.5,
            NodeType.ALERT: 2.0,
            NodeType.MODEL: 1.8,
            NodeType.METRIC: 1.3,
            NodeType.EXPORT: 1.2,
            NodeType.STORAGE: 1.0,
            NodeType.TRANSFORM: 0.8,
            NodeType.AGGREGATION: 0.9,
        }

        logger.info("Impact Analyzer initialized")

    def analyze_impact(
        self,
        node_id: str,
        change_type: str = "modification"
    ) -> ImpactAnalysis:
        """
        Analyze the downstream impact of changing a node.

        Args:
            node_id: The node being changed
            change_type: Type of change (modification, removal, schema_change)

        Returns:
            Impact analysis report
        """
        node = self._graph_manager.get_node(node_id)
        if not node:
            return ImpactAnalysis(
                source_node_id=node_id,
                source_node_name="Unknown",
                risk_level="unknown",
            )

        # Get all downstream nodes
        downstream = self._graph_manager.get_downstream(node_id)

        affected_nodes = []
        affected_visualizations = []
        affected_alerts = []
        affected_models = []
        max_distance = 0

        for downstream_node, distance in downstream:
            affected_nodes.append({
                "node_id": downstream_node.node_id,
                "name": downstream_node.name,
                "type": downstream_node.node_type.value,
                "system": downstream_node.system,
                "distance": distance,
            })

            max_distance = max(max_distance, distance)

            if downstream_node.node_type == NodeType.VISUALIZATION:
                affected_visualizations.append(downstream_node.name)
            elif downstream_node.node_type == NodeType.ALERT:
                affected_alerts.append(downstream_node.name)
            elif downstream_node.node_type == NodeType.MODEL:
                affected_models.append(downstream_node.name)

        # Calculate risk level
        risk_score = self._calculate_risk_score(
            node, downstream, change_type
        )

        if risk_score >= 8:
            risk_level = "critical"
        elif risk_score >= 5:
            risk_level = "high"
        elif risk_score >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            node, downstream, change_type, risk_level
        )

        return ImpactAnalysis(
            source_node_id=node_id,
            source_node_name=node.name,
            affected_nodes=affected_nodes,
            affected_visualizations=affected_visualizations,
            affected_alerts=affected_alerts,
            affected_models=affected_models,
            total_affected=len(affected_nodes),
            max_distance=max_distance,
            risk_level=risk_level,
            recommendations=recommendations,
        )

    def _calculate_risk_score(
        self,
        source_node: LineageNode,
        downstream: List[tuple],
        change_type: str
    ) -> float:
        """Calculate risk score for a change."""
        score = 0.0

        # Base score from change type
        change_weights = {
            "modification": 1.0,
            "schema_change": 2.0,
            "removal": 3.0,
            "deprecation": 1.5,
        }
        score += change_weights.get(change_type, 1.0)

        # Score from affected nodes
        for node, distance in downstream:
            weight = self._risk_weights.get(node.node_type, 1.0)
            # Closer nodes have higher impact
            distance_factor = 1.0 / (distance + 1)
            score += weight * distance_factor

        # Score from source node type
        if source_node.node_type == NodeType.SOURCE:
            score *= 1.5  # Source changes are more impactful

        return score

    def _generate_recommendations(
        self,
        source_node: LineageNode,
        downstream: List[tuple],
        change_type: str,
        risk_level: str
    ) -> List[str]:
        """Generate change recommendations."""
        recommendations = []

        if risk_level in ["high", "critical"]:
            recommendations.append(
                "Planifier cette modification pendant une fenêtre de maintenance"
            )
            recommendations.append(
                "Informer toutes les équipes utilisant les visualisations affectées"
            )

        if change_type == "schema_change":
            recommendations.append(
                "Vérifier la compatibilité des transformations en aval"
            )
            recommendations.append(
                "Mettre à jour les définitions de KPI concernées"
            )

        if change_type == "removal":
            recommendations.append(
                "Identifier des sources alternatives pour les consommateurs"
            )
            recommendations.append(
                "Archiver les données historiques avant suppression"
            )

        # Node type specific recommendations
        affected_types = set(node.node_type for node, _ in downstream)

        if NodeType.ALERT in affected_types:
            recommendations.append(
                "Réviser les seuils d'alerte après modification"
            )

        if NodeType.MODEL in affected_types:
            recommendations.append(
                "Planifier une ré-évaluation des modèles ML affectés"
            )

        if NodeType.VISUALIZATION in affected_types:
            recommendations.append(
                "Tester les tableaux de bord après déploiement"
            )

        return recommendations[:6]  # Limit to 6 recommendations

    def track_provenance(
        self,
        data_id: str,
        value: Any,
        source_node_id: str,
    ) -> Optional[DataProvenance]:
        """
        Track the provenance of a data point.

        Args:
            data_id: Unique identifier for the data
            value: The data value
            source_node_id: The originating node

        Returns:
            Provenance information
        """
        source_node = self._graph_manager.get_node(source_node_id)
        if not source_node:
            return None

        # Find path to sinks
        sinks = self._graph_manager.get_sinks()
        if not sinks:
            path = DataFlowPath(nodes=[source_node_id])
        else:
            # Use first sink as example
            path = self._graph_manager.find_path(source_node_id, sinks[0].node_id)
            if not path:
                path = DataFlowPath(nodes=[source_node_id])

        # Collect transformations
        transformations = []
        for edge in self._graph_manager.graph.edges:
            if edge.edge_id in path.edges and edge.transformation:
                transformations.append(edge.transformation)

        # Calculate quality
        quality = self._assess_data_quality(source_node, path)

        return DataProvenance(
            data_id=data_id,
            value=value,
            timestamp=datetime.utcnow(),
            source_node_id=source_node_id,
            source_system=source_node.system,
            path=path,
            transformations_applied=transformations,
            quality=quality,
        )

    def _assess_data_quality(
        self,
        source_node: LineageNode,
        path: DataFlowPath
    ) -> DataQuality:
        """Assess data quality based on source and path."""
        # Start with source quality
        if source_node.data_quality != DataQuality.UNKNOWN:
            return source_node.data_quality

        # Infer from path length (more transformations = more risk)
        if path.transformation_count == 0:
            return DataQuality.GOOD
        elif path.transformation_count <= 2:
            return DataQuality.GOOD
        elif path.transformation_count <= 5:
            return DataQuality.ACCEPTABLE
        else:
            return DataQuality.ACCEPTABLE

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate a data quality report for the entire lineage."""
        quality_counts = defaultdict(int)
        system_quality = defaultdict(list)
        issues = []

        for node in self._graph_manager.graph.nodes.values():
            quality = node.data_quality
            quality_counts[quality.value] += 1

            if node.system:
                system_quality[node.system].append(quality)

            # Check for quality issues
            if quality == DataQuality.POOR:
                issues.append({
                    "node_id": node.node_id,
                    "name": node.name,
                    "issue": "Qualité de données faible",
                    "recommendation": "Vérifier la source et les transformations",
                })

            if node.freshness_seconds and node.freshness_seconds > 3600:
                issues.append({
                    "node_id": node.node_id,
                    "name": node.name,
                    "issue": "Données potentiellement obsolètes",
                    "recommendation": "Vérifier la fréquence de mise à jour",
                })

        # Calculate system scores
        system_scores = {}
        for system, qualities in system_quality.items():
            quality_values = {
                DataQuality.EXCELLENT: 4,
                DataQuality.GOOD: 3,
                DataQuality.ACCEPTABLE: 2,
                DataQuality.POOR: 1,
                DataQuality.UNKNOWN: 2,
            }
            avg_score = sum(quality_values.get(q, 2) for q in qualities) / len(qualities)
            system_scores[system] = round(avg_score, 2)

        return {
            "quality_distribution": dict(quality_counts),
            "system_scores": system_scores,
            "issues": issues,
            "total_nodes": len(self._graph_manager.graph.nodes),
            "nodes_with_issues": len(issues),
        }

    def find_critical_paths(self) -> List[Dict[str, Any]]:
        """Find critical data paths (source to important sinks)."""
        critical_paths = []

        sources = self._graph_manager.get_sources()
        sinks = self._graph_manager.get_sinks()

        # Filter for critical sinks (alerts, dashboards)
        critical_sinks = [
            s for s in sinks
            if s.node_type in [NodeType.ALERT, NodeType.VISUALIZATION, NodeType.MODEL]
        ]

        for source in sources:
            for sink in critical_sinks:
                path = self._graph_manager.find_path(source.node_id, sink.node_id)
                if path:
                    # Calculate path risk
                    intermediate_nodes = []
                    for node_id in path.nodes[1:-1]:
                        node = self._graph_manager.get_node(node_id)
                        if node:
                            intermediate_nodes.append(node.name)

                    critical_paths.append({
                        "source": source.name,
                        "sink": sink.name,
                        "sink_type": sink.node_type.value,
                        "path_length": len(path.nodes),
                        "transformations": path.transformation_count,
                        "intermediate_nodes": intermediate_nodes,
                        "path_id": path.path_id,
                    })

        # Sort by sink type importance
        type_priority = {
            NodeType.ALERT: 0,
            NodeType.MODEL: 1,
            NodeType.VISUALIZATION: 2,
        }
        critical_paths.sort(
            key=lambda p: type_priority.get(NodeType(p["sink_type"]), 99)
        )

        return critical_paths

    def suggest_improvements(self) -> List[Dict[str, Any]]:
        """Suggest improvements to the data lineage."""
        suggestions = []

        # Check for long paths
        sources = self._graph_manager.get_sources()
        for source in sources:
            downstream = self._graph_manager.get_downstream(source.node_id)
            long_paths = [(n, d) for n, d in downstream if d > 5]

            if long_paths:
                suggestions.append({
                    "type": "optimization",
                    "title": "Chemin de données long détecté",
                    "description": f"La source '{source.name}' a des chemins de plus de 5 transformations",
                    "recommendation": "Considérer la consolidation des transformations",
                    "affected_nodes": [n.name for n, _ in long_paths[:3]],
                })

        # Check for nodes without documentation
        undocumented = [
            n for n in self._graph_manager.graph.nodes.values()
            if not n.description and not n.schema_fields
        ]

        if len(undocumented) > len(self._graph_manager.graph.nodes) * 0.3:
            suggestions.append({
                "type": "documentation",
                "title": "Documentation insuffisante",
                "description": f"{len(undocumented)} nœuds n'ont pas de documentation",
                "recommendation": "Ajouter des descriptions et schémas aux nœuds",
                "affected_nodes": [n.name for n in undocumented[:5]],
            })

        # Check for single points of failure
        for node_id, node in self._graph_manager.graph.nodes.items():
            if node.node_type in [NodeType.TRANSFORM, NodeType.AGGREGATION]:
                downstream = self._graph_manager.get_downstream(node_id)
                critical_downstream = [
                    n for n, _ in downstream
                    if n.node_type in [NodeType.ALERT, NodeType.VISUALIZATION]
                ]

                if len(critical_downstream) >= 3:
                    suggestions.append({
                        "type": "resilience",
                        "title": "Point unique de défaillance potentiel",
                        "description": f"'{node.name}' alimente {len(critical_downstream)} éléments critiques",
                        "recommendation": "Considérer une redondance ou un fallback",
                        "affected_nodes": [n.name for n in critical_downstream[:3]],
                    })

        return suggestions
