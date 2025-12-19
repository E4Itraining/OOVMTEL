"""
Data Lineage Engine - Main engine for data lineage tracking
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from .models import (
    LineageNode,
    LineageEdge,
    LineageGraph,
    LineageSnapshot,
    ImpactAnalysis,
    DataProvenance,
    NodeType,
    EdgeType,
    STANDARD_DATA_SOURCES,
    TRANSFORMATION_TYPES,
)
from .graph_manager import GraphManager
from .impact_analyzer import ImpactAnalyzer

logger = logging.getLogger(__name__)


class DataLineageEngine:
    """
    Main Data Lineage Engine for SYNAPSIX.

    Features:
    - Track data flow from source to visualization
    - Impact analysis for changes
    - Provenance tracking
    - Graph visualization export
    - Lineage snapshots
    """

    def __init__(self):
        self._graph_manager = GraphManager()
        self._impact_analyzer = ImpactAnalyzer(self._graph_manager)
        self._snapshots: List[LineageSnapshot] = []

        logger.info("Data Lineage Engine initialized")

    @property
    def graph(self) -> LineageGraph:
        """Get current lineage graph."""
        return self._graph_manager.graph

    # Node management

    def register_source(
        self,
        name: str,
        system: str,
        location: str = "",
        description: str = "",
        schema_fields: Optional[List[Dict[str, str]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
    ) -> LineageNode:
        """
        Register a data source.

        Args:
            name: Source name
            system: System name (e.g., "OPC-UA", "MQTT")
            location: Path or identifier
            description: Description
            schema_fields: Schema definition
            properties: Additional properties
            template: Template to use (from STANDARD_DATA_SOURCES)

        Returns:
            Created node
        """
        node_props = properties or {}

        # Apply template if specified
        if template and template in STANDARD_DATA_SOURCES:
            tpl = STANDARD_DATA_SOURCES[template]
            node_props.update(tpl.properties)

        return self._graph_manager.add_node(
            name=name,
            node_type=NodeType.SOURCE,
            description=description,
            system=system,
            location=location,
            properties=node_props,
            schema_fields=schema_fields,
        )

    def register_transformation(
        self,
        name: str,
        transformation_type: str,
        source_node_ids: List[str],
        description: str = "",
        formula: Optional[str] = None,
    ) -> Optional[LineageNode]:
        """
        Register a transformation step.

        Args:
            name: Transformation name
            transformation_type: Type (filter, aggregate, join, etc.)
            source_node_ids: Input node IDs
            description: Description
            formula: Transformation formula/SQL

        Returns:
            Created node and edges
        """
        # Get transformation info
        trans_info = TRANSFORMATION_TYPES.get(transformation_type, {})

        node = self._graph_manager.add_node(
            name=name,
            node_type=NodeType.TRANSFORM,
            description=description or trans_info.get("description", ""),
            properties={
                "transformation_type": transformation_type,
                "formula": formula,
            },
        )

        # Create edges from sources
        for source_id in source_node_ids:
            self._graph_manager.add_edge(
                source_node_id=source_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.FLOW,
                transformation=formula,
                transformation_type=transformation_type,
            )

        return node

    def register_metric(
        self,
        name: str,
        source_node_ids: List[str],
        formula: str = "",
        description: str = "",
        unit: str = "",
    ) -> Optional[LineageNode]:
        """Register a calculated metric."""
        node = self._graph_manager.add_node(
            name=name,
            node_type=NodeType.METRIC,
            description=description,
            properties={
                "formula": formula,
                "unit": unit,
            },
        )

        for source_id in source_node_ids:
            self._graph_manager.add_edge(
                source_node_id=source_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.DERIVES,
                transformation=formula,
                transformation_type="calculate",
            )

        return node

    def register_storage(
        self,
        name: str,
        system: str,
        source_node_ids: List[str],
        location: str = "",
        description: str = "",
        retention_days: Optional[int] = None,
    ) -> Optional[LineageNode]:
        """Register a storage destination."""
        node = self._graph_manager.add_node(
            name=name,
            node_type=NodeType.STORAGE,
            description=description,
            system=system,
            location=location,
            properties={
                "retention_days": retention_days,
            },
        )

        for source_id in source_node_ids:
            self._graph_manager.add_edge(
                source_node_id=source_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.FLOW,
            )

        return node

    def register_visualization(
        self,
        name: str,
        source_node_ids: List[str],
        dashboard_name: str = "",
        chart_type: str = "",
        description: str = "",
    ) -> Optional[LineageNode]:
        """Register a visualization (dashboard, chart)."""
        node = self._graph_manager.add_node(
            name=name,
            node_type=NodeType.VISUALIZATION,
            description=description,
            system="SYNAPSIX",
            properties={
                "dashboard": dashboard_name,
                "chart_type": chart_type,
            },
        )

        for source_id in source_node_ids:
            self._graph_manager.add_edge(
                source_node_id=source_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.USES,
            )

        return node

    def register_alert(
        self,
        name: str,
        source_node_ids: List[str],
        condition: str = "",
        severity: str = "warning",
        description: str = "",
    ) -> Optional[LineageNode]:
        """Register an alert definition."""
        node = self._graph_manager.add_node(
            name=name,
            node_type=NodeType.ALERT,
            description=description,
            properties={
                "condition": condition,
                "severity": severity,
            },
        )

        for source_id in source_node_ids:
            self._graph_manager.add_edge(
                source_node_id=source_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.TRIGGERS,
            )

        return node

    def register_model(
        self,
        name: str,
        source_node_ids: List[str],
        model_type: str = "",
        version: str = "",
        description: str = "",
    ) -> Optional[LineageNode]:
        """Register an ML model."""
        node = self._graph_manager.add_node(
            name=name,
            node_type=NodeType.MODEL,
            description=description,
            properties={
                "model_type": model_type,
                "version": version,
            },
        )

        for source_id in source_node_ids:
            self._graph_manager.add_edge(
                source_node_id=source_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.USES,
            )

        return node

    # Lineage queries

    def get_upstream(
        self,
        node_id: str,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all upstream nodes (data sources)."""
        upstream = self._graph_manager.get_upstream(node_id, max_depth)
        return [
            {
                "node_id": node.node_id,
                "name": node.name,
                "type": node.node_type.value,
                "system": node.system,
                "distance": distance,
            }
            for node, distance in upstream
        ]

    def get_downstream(
        self,
        node_id: str,
        max_depth: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all downstream nodes (consumers)."""
        downstream = self._graph_manager.get_downstream(node_id, max_depth)
        return [
            {
                "node_id": node.node_id,
                "name": node.name,
                "type": node.node_type.value,
                "system": node.system,
                "distance": distance,
            }
            for node, distance in downstream
        ]

    def trace_data(
        self,
        source_node_id: str,
        target_node_id: str
    ) -> Optional[Dict[str, Any]]:
        """Trace data flow between two nodes."""
        path = self._graph_manager.find_path(source_node_id, target_node_id)
        if not path:
            return None

        # Build detailed path
        detailed_nodes = []
        for node_id in path.nodes:
            node = self._graph_manager.get_node(node_id)
            if node:
                detailed_nodes.append({
                    "node_id": node.node_id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "system": node.system,
                })

        transformations = []
        for edge in self._graph_manager.graph.edges:
            if edge.edge_id in path.edges:
                transformations.append({
                    "from": edge.source_node_id,
                    "to": edge.target_node_id,
                    "type": edge.transformation_type,
                    "formula": edge.transformation,
                })

        return {
            "path_id": path.path_id,
            "nodes": detailed_nodes,
            "transformations": transformations,
            "total_steps": len(path.nodes) - 1,
        }

    # Impact analysis

    def analyze_change_impact(
        self,
        node_id: str,
        change_type: str = "modification"
    ) -> ImpactAnalysis:
        """Analyze the impact of changing a node."""
        return self._impact_analyzer.analyze_impact(node_id, change_type)

    def get_critical_paths(self) -> List[Dict[str, Any]]:
        """Get critical data paths."""
        return self._impact_analyzer.find_critical_paths()

    def get_quality_report(self) -> Dict[str, Any]:
        """Get data quality report."""
        return self._impact_analyzer.get_data_quality_report()

    def get_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Get improvement suggestions."""
        return self._impact_analyzer.suggest_improvements()

    # Snapshots

    def take_snapshot(self, description: str = "") -> LineageSnapshot:
        """Take a snapshot of current lineage state."""
        graph = self._graph_manager.graph

        snapshot = LineageSnapshot(
            timestamp=datetime.utcnow(),
            graph=graph.model_copy(deep=True),
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            source_count=len([n for n in graph.nodes.values() if n.node_type == NodeType.SOURCE]),
            visualization_count=len([n for n in graph.nodes.values() if n.node_type == NodeType.VISUALIZATION]),
        )

        # Calculate path statistics
        sources = self._graph_manager.get_sources()
        sinks = self._graph_manager.get_sinks()
        active_paths = 0
        for source in sources:
            for sink in sinks:
                if self._graph_manager.find_path(source.node_id, sink.node_id):
                    active_paths += 1

        snapshot.active_paths = active_paths
        snapshot.deprecated_nodes = len([n for n in graph.nodes.values() if n.is_deprecated])

        self._snapshots.append(snapshot)

        # Keep last 100 snapshots
        if len(self._snapshots) > 100:
            self._snapshots = self._snapshots[-100:]

        logger.info(f"Created lineage snapshot: {snapshot.snapshot_id}")
        return snapshot

    def get_snapshots(self, limit: int = 10) -> List[LineageSnapshot]:
        """Get recent snapshots."""
        return self._snapshots[-limit:]

    def compare_snapshots(
        self,
        snapshot_id_1: str,
        snapshot_id_2: str
    ) -> Dict[str, Any]:
        """Compare two snapshots."""
        snap1 = None
        snap2 = None

        for s in self._snapshots:
            if s.snapshot_id == snapshot_id_1:
                snap1 = s
            if s.snapshot_id == snapshot_id_2:
                snap2 = s

        if not snap1 or not snap2:
            return {"error": "Snapshot not found"}

        # Compare nodes
        nodes1 = set(snap1.graph.nodes.keys())
        nodes2 = set(snap2.graph.nodes.keys())

        added_nodes = nodes2 - nodes1
        removed_nodes = nodes1 - nodes2

        # Compare edges
        edges1 = {(e.source_node_id, e.target_node_id) for e in snap1.graph.edges}
        edges2 = {(e.source_node_id, e.target_node_id) for e in snap2.graph.edges}

        added_edges = edges2 - edges1
        removed_edges = edges1 - edges2

        return {
            "snapshot_1": {
                "id": snapshot_id_1,
                "timestamp": snap1.timestamp.isoformat(),
                "node_count": snap1.node_count,
                "edge_count": snap1.edge_count,
            },
            "snapshot_2": {
                "id": snapshot_id_2,
                "timestamp": snap2.timestamp.isoformat(),
                "node_count": snap2.node_count,
                "edge_count": snap2.edge_count,
            },
            "changes": {
                "nodes_added": len(added_nodes),
                "nodes_removed": len(removed_nodes),
                "edges_added": len(added_edges),
                "edges_removed": len(removed_edges),
            },
            "added_nodes": list(added_nodes),
            "removed_nodes": list(removed_nodes),
        }

    # Export

    def export_for_visualization(self) -> Dict[str, Any]:
        """Export lineage for graph visualization."""
        return self._graph_manager.export_graph()

    def export_to_json(self) -> str:
        """Export lineage to JSON."""
        data = {
            "graph": self._graph_manager.graph.model_dump(),
            "statistics": self._graph_manager.get_statistics(),
            "exported_at": datetime.utcnow().isoformat(),
        }
        return json.dumps(data, default=str, indent=2)

    def import_from_json(self, json_data: str) -> bool:
        """Import lineage from JSON."""
        try:
            data = json.loads(json_data)
            graph_data = data.get("graph", {})

            # Import nodes
            for node_id, node_data in graph_data.get("nodes", {}).items():
                node = LineageNode(**node_data)
                self._graph_manager._graph.nodes[node_id] = node

            # Import edges
            for edge_data in graph_data.get("edges", []):
                edge = LineageEdge(**edge_data)
                self._graph_manager._graph.edges.append(edge)
                self._graph_manager._adjacency[edge.source_node_id].add(edge.target_node_id)
                self._graph_manager._reverse_adjacency[edge.target_node_id].add(edge.source_node_id)

            logger.info("Imported lineage from JSON")
            return True

        except Exception as e:
            logger.error(f"Failed to import lineage: {e}")
            return False

    # Utilities

    def get_node(self, node_id: str) -> Optional[LineageNode]:
        """Get a node by ID."""
        return self._graph_manager.get_node(node_id)

    def find_nodes(
        self,
        node_type: Optional[NodeType] = None,
        system: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> List[LineageNode]:
        """Find nodes matching criteria."""
        return self._graph_manager.find_nodes(
            node_type=node_type,
            system=system,
            name_contains=name_contains,
        )

    def validate(self) -> Dict[str, Any]:
        """Validate the lineage graph."""
        return self._graph_manager.validate_graph()

    def get_statistics(self) -> Dict[str, Any]:
        """Get lineage statistics."""
        return self._graph_manager.get_statistics()

    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent lineage events."""
        events = self._graph_manager.get_events(limit)
        return [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "type": e.event_type,
                "description": e.description,
                "node_id": e.node_id,
                "edge_id": e.edge_id,
            }
            for e in events
        ]
