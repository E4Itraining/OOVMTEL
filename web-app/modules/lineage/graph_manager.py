"""
Graph Manager - Build and traverse lineage graphs
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, deque

from .models import (
    LineageNode,
    LineageEdge,
    LineageGraph,
    DataFlowPath,
    ImpactAnalysis,
    LineageEvent,
    NodeType,
    EdgeType,
    DataQuality,
)

logger = logging.getLogger(__name__)


class GraphManager:
    """
    Manage lineage graph operations.

    Features:
    - Node and edge management
    - Graph traversal (upstream/downstream)
    - Path finding
    - Cycle detection
    - Graph validation
    """

    def __init__(self):
        self._graph = LineageGraph()
        self._adjacency: Dict[str, Set[str]] = defaultdict(set)  # Forward edges
        self._reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)  # Backward edges
        self._events: List[LineageEvent] = []

        logger.info("Graph Manager initialized")

    @property
    def graph(self) -> LineageGraph:
        """Get current graph."""
        return self._graph

    # Node operations

    def add_node(
        self,
        name: str,
        node_type: NodeType,
        description: str = "",
        system: str = "",
        location: str = "",
        properties: Optional[Dict[str, Any]] = None,
        schema_fields: Optional[List[Dict[str, str]]] = None,
        node_id: Optional[str] = None,
    ) -> LineageNode:
        """Add a node to the graph."""
        node = LineageNode(
            name=name,
            node_type=node_type,
            description=description,
            system=system,
            location=location,
            properties=properties or {},
            schema_fields=schema_fields or [],
        )

        if node_id:
            node.node_id = node_id

        self._graph.nodes[node.node_id] = node
        self._graph.updated_at = datetime.utcnow()

        self._record_event("node_added", node_id=node.node_id,
                          description=f"Added node: {name}")

        logger.info(f"Added node: {name} ({node.node_id})")
        return node

    def update_node(
        self,
        node_id: str,
        **updates
    ) -> Optional[LineageNode]:
        """Update a node."""
        if node_id not in self._graph.nodes:
            return None

        node = self._graph.nodes[node_id]
        old_values = {}

        for key, value in updates.items():
            if hasattr(node, key):
                old_values[key] = getattr(node, key)
                setattr(node, key, value)

        node.last_seen = datetime.utcnow()
        self._graph.updated_at = datetime.utcnow()

        self._record_event("node_updated", node_id=node_id,
                          description=f"Updated node: {node.name}",
                          old_value=old_values, new_value=updates)

        return node

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its edges."""
        if node_id not in self._graph.nodes:
            return False

        node = self._graph.nodes[node_id]

        # Remove edges
        self._graph.edges = [
            e for e in self._graph.edges
            if e.source_node_id != node_id and e.target_node_id != node_id
        ]

        # Update adjacency
        if node_id in self._adjacency:
            del self._adjacency[node_id]
        if node_id in self._reverse_adjacency:
            del self._reverse_adjacency[node_id]

        for adj in self._adjacency.values():
            adj.discard(node_id)
        for adj in self._reverse_adjacency.values():
            adj.discard(node_id)

        # Remove node
        del self._graph.nodes[node_id]
        self._graph.updated_at = datetime.utcnow()

        self._record_event("node_removed", node_id=node_id,
                          description=f"Removed node: {node.name}")

        logger.info(f"Removed node: {node_id}")
        return True

    def get_node(self, node_id: str) -> Optional[LineageNode]:
        """Get a node by ID."""
        return self._graph.nodes.get(node_id)

    def find_nodes(
        self,
        node_type: Optional[NodeType] = None,
        system: Optional[str] = None,
        tags: Optional[List[str]] = None,
        name_contains: Optional[str] = None,
    ) -> List[LineageNode]:
        """Find nodes matching criteria."""
        nodes = list(self._graph.nodes.values())

        if node_type:
            nodes = [n for n in nodes if n.node_type == node_type]

        if system:
            nodes = [n for n in nodes if n.system == system]

        if tags:
            nodes = [n for n in nodes if any(t in n.tags for t in tags)]

        if name_contains:
            name_lower = name_contains.lower()
            nodes = [n for n in nodes if name_lower in n.name.lower()]

        return nodes

    # Edge operations

    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: EdgeType = EdgeType.FLOW,
        transformation: Optional[str] = None,
        transformation_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[LineageEdge]:
        """Add an edge between nodes."""
        if source_node_id not in self._graph.nodes:
            logger.error(f"Source node not found: {source_node_id}")
            return None

        if target_node_id not in self._graph.nodes:
            logger.error(f"Target node not found: {target_node_id}")
            return None

        # Check for duplicate
        for edge in self._graph.edges:
            if edge.source_node_id == source_node_id and edge.target_node_id == target_node_id:
                logger.warning(f"Edge already exists: {source_node_id} -> {target_node_id}")
                return edge

        edge = LineageEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            transformation=transformation,
            transformation_type=transformation_type,
            properties=properties or {},
        )

        self._graph.edges.append(edge)
        self._adjacency[source_node_id].add(target_node_id)
        self._reverse_adjacency[target_node_id].add(source_node_id)
        self._graph.updated_at = datetime.utcnow()

        self._record_event("edge_added", edge_id=edge.edge_id,
                          description=f"Added edge: {source_node_id} -> {target_node_id}")

        logger.info(f"Added edge: {source_node_id} -> {target_node_id}")
        return edge

    def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge."""
        edge = None
        for e in self._graph.edges:
            if e.edge_id == edge_id:
                edge = e
                break

        if not edge:
            return False

        self._graph.edges.remove(edge)
        self._adjacency[edge.source_node_id].discard(edge.target_node_id)
        self._reverse_adjacency[edge.target_node_id].discard(edge.source_node_id)
        self._graph.updated_at = datetime.utcnow()

        self._record_event("edge_removed", edge_id=edge_id,
                          description=f"Removed edge: {edge.source_node_id} -> {edge.target_node_id}")

        return True

    # Graph traversal

    def get_downstream(
        self,
        node_id: str,
        max_depth: int = 10
    ) -> List[Tuple[LineageNode, int]]:
        """
        Get all downstream nodes (nodes that depend on this node).

        Returns list of (node, distance) tuples.
        """
        if node_id not in self._graph.nodes:
            return []

        visited = set()
        result = []
        queue = deque([(node_id, 0)])

        while queue:
            current_id, depth = queue.popleft()

            if depth > max_depth:
                continue

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id != node_id:
                node = self._graph.nodes.get(current_id)
                if node:
                    result.append((node, depth))

            # Add neighbors
            for neighbor_id in self._adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, depth + 1))

        return sorted(result, key=lambda x: x[1])

    def get_upstream(
        self,
        node_id: str,
        max_depth: int = 10
    ) -> List[Tuple[LineageNode, int]]:
        """
        Get all upstream nodes (nodes this node depends on).

        Returns list of (node, distance) tuples.
        """
        if node_id not in self._graph.nodes:
            return []

        visited = set()
        result = []
        queue = deque([(node_id, 0)])

        while queue:
            current_id, depth = queue.popleft()

            if depth > max_depth:
                continue

            if current_id in visited:
                continue
            visited.add(current_id)

            if current_id != node_id:
                node = self._graph.nodes.get(current_id)
                if node:
                    result.append((node, depth))

            # Add reverse neighbors
            for neighbor_id in self._reverse_adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, depth + 1))

        return sorted(result, key=lambda x: x[1])

    def find_path(
        self,
        source_node_id: str,
        target_node_id: str
    ) -> Optional[DataFlowPath]:
        """Find a path between two nodes."""
        if source_node_id not in self._graph.nodes:
            return None
        if target_node_id not in self._graph.nodes:
            return None

        # BFS to find shortest path
        visited = set()
        queue = deque([(source_node_id, [source_node_id])])

        while queue:
            current_id, path = queue.popleft()

            if current_id == target_node_id:
                # Build path object
                edges = []
                for i in range(len(path) - 1):
                    for edge in self._graph.edges:
                        if edge.source_node_id == path[i] and edge.target_node_id == path[i + 1]:
                            edges.append(edge.edge_id)
                            break

                return DataFlowPath(
                    nodes=path,
                    edges=edges,
                    transformation_count=len(edges),
                )

            if current_id in visited:
                continue
            visited.add(current_id)

            for neighbor_id in self._adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    def find_all_paths(
        self,
        source_node_id: str,
        target_node_id: str,
        max_paths: int = 10
    ) -> List[DataFlowPath]:
        """Find all paths between two nodes (up to max_paths)."""
        if source_node_id not in self._graph.nodes:
            return []
        if target_node_id not in self._graph.nodes:
            return []

        paths = []

        def dfs(current: str, path: List[str], visited: Set[str]):
            if len(paths) >= max_paths:
                return

            if current == target_node_id:
                edges = []
                for i in range(len(path) - 1):
                    for edge in self._graph.edges:
                        if edge.source_node_id == path[i] and edge.target_node_id == path[i + 1]:
                            edges.append(edge.edge_id)
                            break

                paths.append(DataFlowPath(
                    nodes=path.copy(),
                    edges=edges,
                    transformation_count=len(edges),
                ))
                return

            for neighbor_id in self._adjacency.get(current, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    path.append(neighbor_id)
                    dfs(neighbor_id, path, visited)
                    path.pop()
                    visited.remove(neighbor_id)

        dfs(source_node_id, [source_node_id], {source_node_id})
        return paths

    # Analysis

    def get_sources(self) -> List[LineageNode]:
        """Get all source nodes (no incoming edges)."""
        return [
            node for node_id, node in self._graph.nodes.items()
            if not self._reverse_adjacency.get(node_id)
            or node.node_type == NodeType.SOURCE
        ]

    def get_sinks(self) -> List[LineageNode]:
        """Get all sink nodes (no outgoing edges)."""
        return [
            node for node_id, node in self._graph.nodes.items()
            if not self._adjacency.get(node_id)
            or node.node_type in [NodeType.VISUALIZATION, NodeType.EXPORT, NodeType.ALERT]
        ]

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the graph."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: str, path: List[str]) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for neighbor_id in self._adjacency.get(node_id, []):
                if neighbor_id not in visited:
                    if dfs(neighbor_id, path):
                        return True
                elif neighbor_id in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor_id)
                    cycles.append(path[cycle_start:] + [neighbor_id])

            path.pop()
            rec_stack.remove(node_id)
            return False

        for node_id in self._graph.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles

    def validate_graph(self) -> Dict[str, Any]:
        """Validate graph integrity."""
        issues = []

        # Check for orphaned nodes
        for node_id, node in self._graph.nodes.items():
            if not self._adjacency.get(node_id) and not self._reverse_adjacency.get(node_id):
                if node.node_type not in [NodeType.SOURCE, NodeType.VISUALIZATION]:
                    issues.append({
                        "type": "orphan",
                        "node_id": node_id,
                        "message": f"Node {node.name} has no connections",
                    })

        # Check for cycles
        cycles = self.detect_cycles()
        for cycle in cycles:
            issues.append({
                "type": "cycle",
                "nodes": cycle,
                "message": f"Cycle detected: {' -> '.join(cycle)}",
            })

        # Check edge references
        for edge in self._graph.edges:
            if edge.source_node_id not in self._graph.nodes:
                issues.append({
                    "type": "missing_source",
                    "edge_id": edge.edge_id,
                    "message": f"Edge references missing source: {edge.source_node_id}",
                })
            if edge.target_node_id not in self._graph.nodes:
                issues.append({
                    "type": "missing_target",
                    "edge_id": edge.edge_id,
                    "message": f"Edge references missing target: {edge.target_node_id}",
                })

        return {
            "valid": len(issues) == 0,
            "node_count": len(self._graph.nodes),
            "edge_count": len(self._graph.edges),
            "issues": issues,
        }

    def _record_event(
        self,
        event_type: str,
        node_id: Optional[str] = None,
        edge_id: Optional[str] = None,
        description: str = "",
        old_value: Any = None,
        new_value: Any = None,
    ) -> None:
        """Record a lineage event."""
        event = LineageEvent(
            event_type=event_type,
            node_id=node_id,
            edge_id=edge_id,
            description=description,
            old_value=old_value,
            new_value=new_value,
        )
        self._events.append(event)

        # Keep last 1000 events
        if len(self._events) > 1000:
            self._events = self._events[-1000:]

    def get_events(self, limit: int = 100) -> List[LineageEvent]:
        """Get recent events."""
        return self._events[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        node_types = defaultdict(int)
        for node in self._graph.nodes.values():
            node_types[node.node_type.value] += 1

        systems = defaultdict(int)
        for node in self._graph.nodes.values():
            if node.system:
                systems[node.system] += 1

        return {
            "total_nodes": len(self._graph.nodes),
            "total_edges": len(self._graph.edges),
            "node_types": dict(node_types),
            "systems": dict(systems),
            "sources": len(self.get_sources()),
            "sinks": len(self.get_sinks()),
            "cycles": len(self.detect_cycles()),
        }

    def export_graph(self) -> Dict[str, Any]:
        """Export graph for visualization."""
        nodes = []
        for node in self._graph.nodes.values():
            nodes.append({
                "id": node.node_id,
                "label": node.name,
                "type": node.node_type.value,
                "system": node.system,
                "properties": node.properties,
            })

        edges = []
        for edge in self._graph.edges:
            edges.append({
                "id": edge.edge_id,
                "source": edge.source_node_id,
                "target": edge.target_node_id,
                "type": edge.edge_type.value,
                "label": edge.transformation_type or "",
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": self.get_statistics(),
        }
