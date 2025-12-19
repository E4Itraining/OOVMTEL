"""
Assistant Tools Module (Function Calling).

Defines callable tools/functions that the AI assistant can use
to interact with the SYNAPSIX platform.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Categories of assistant tools."""
    METRICS = "metrics"
    EQUIPMENT = "equipment"
    ALERTS = "alerts"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"
    ANALYSIS = "analysis"
    SYSTEM = "system"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str  # string, number, boolean, array, object
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    items: Optional[Dict[str, Any]] = None  # For array type

    def to_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema = {
            "type": self.type,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.items and self.type == "array":
            schema["items"] = self.items
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class Tool:
    """Definition of an assistant tool."""
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: str = "object"
    handler: Optional[Callable] = None
    requires_confirmation: bool = False
    is_async: bool = True

    def to_function_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI/Mistral function schema format."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


class ToolRegistry:
    """
    Registry of available tools for the assistant.

    Manages tool definitions and execution.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register the default set of industrial tools."""

        # =======================================================================
        # METRICS TOOLS
        # =======================================================================

        self.register(Tool(
            name="get_current_metrics",
            description="Récupère les métriques actuelles pour un équipement ou une ligne de production",
            category=ToolCategory.METRICS,
            parameters=[
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Identifiant de l'équipement (ex: 'reactor-01', 'line-A')",
                    required=False
                ),
                ToolParameter(
                    name="metric_types",
                    type="array",
                    description="Types de métriques à récupérer",
                    required=False,
                    items={"type": "string", "enum": [
                        "temperature", "pressure", "vibration", "power",
                        "flow_rate", "oee", "availability", "quality", "performance"
                    ]}
                ),
                ToolParameter(
                    name="include_thresholds",
                    type="boolean",
                    description="Inclure les seuils d'alerte",
                    required=False,
                    default=True
                )
            ]
        ))

        self.register(Tool(
            name="get_metric_history",
            description="Récupère l'historique d'une métrique sur une période donnée",
            category=ToolCategory.METRICS,
            parameters=[
                ToolParameter(
                    name="metric_name",
                    type="string",
                    description="Nom de la métrique (ex: 'temperature', 'oee')"
                ),
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Identifiant de l'équipement",
                    required=False
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période (ex: '1h', '24h', '7d', '30d')",
                    default="24h"
                ),
                ToolParameter(
                    name="aggregation",
                    type="string",
                    description="Type d'agrégation",
                    enum=["avg", "min", "max", "sum", "count"],
                    default="avg"
                ),
                ToolParameter(
                    name="interval",
                    type="string",
                    description="Intervalle de points (ex: '5m', '1h')",
                    required=False
                )
            ]
        ))

        self.register(Tool(
            name="compare_metrics",
            description="Compare les métriques entre plusieurs équipements ou périodes",
            category=ToolCategory.METRICS,
            parameters=[
                ToolParameter(
                    name="metric_name",
                    type="string",
                    description="Métrique à comparer"
                ),
                ToolParameter(
                    name="targets",
                    type="array",
                    description="Équipements ou périodes à comparer",
                    items={"type": "string"}
                ),
                ToolParameter(
                    name="comparison_type",
                    type="string",
                    description="Type de comparaison",
                    enum=["equipment", "period", "benchmark"],
                    default="equipment"
                )
            ]
        ))

        # =======================================================================
        # EQUIPMENT TOOLS
        # =======================================================================

        self.register(Tool(
            name="get_equipment_status",
            description="Récupère le statut actuel d'un équipement",
            category=ToolCategory.EQUIPMENT,
            parameters=[
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Identifiant de l'équipement"
                ),
                ToolParameter(
                    name="include_health_score",
                    type="boolean",
                    description="Inclure le score de santé prédictif",
                    default=True
                )
            ]
        ))

        self.register(Tool(
            name="list_equipment",
            description="Liste tous les équipements avec leur statut",
            category=ToolCategory.EQUIPMENT,
            parameters=[
                ToolParameter(
                    name="equipment_type",
                    type="string",
                    description="Filtrer par type d'équipement",
                    required=False,
                    enum=["reactor", "pump", "conveyor", "mixer", "furnace", "tank", "sensor"]
                ),
                ToolParameter(
                    name="status_filter",
                    type="string",
                    description="Filtrer par statut",
                    required=False,
                    enum=["running", "stopped", "warning", "critical", "maintenance"]
                ),
                ToolParameter(
                    name="production_line",
                    type="string",
                    description="Filtrer par ligne de production",
                    required=False
                )
            ]
        ))

        self.register(Tool(
            name="get_equipment_health",
            description="Analyse la santé d'un équipement avec prédiction de maintenance",
            category=ToolCategory.EQUIPMENT,
            parameters=[
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Identifiant de l'équipement"
                ),
                ToolParameter(
                    name="include_recommendations",
                    type="boolean",
                    description="Inclure les recommandations de maintenance",
                    default=True
                )
            ]
        ))

        # =======================================================================
        # ALERTS TOOLS
        # =======================================================================

        self.register(Tool(
            name="get_active_alerts",
            description="Récupère les alertes actives",
            category=ToolCategory.ALERTS,
            parameters=[
                ToolParameter(
                    name="severity",
                    type="string",
                    description="Filtrer par sévérité",
                    required=False,
                    enum=["critical", "warning", "info"]
                ),
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Filtrer par équipement",
                    required=False
                ),
                ToolParameter(
                    name="acknowledged",
                    type="boolean",
                    description="Inclure les alertes acquittées",
                    required=False,
                    default=False
                ),
                ToolParameter(
                    name="limit",
                    type="number",
                    description="Nombre maximum d'alertes",
                    default=20
                )
            ]
        ))

        self.register(Tool(
            name="acknowledge_alert",
            description="Acquitte une alerte (marque comme vue)",
            category=ToolCategory.ALERTS,
            parameters=[
                ToolParameter(
                    name="alert_id",
                    type="string",
                    description="Identifiant de l'alerte"
                ),
                ToolParameter(
                    name="comment",
                    type="string",
                    description="Commentaire optionnel",
                    required=False
                )
            ],
            requires_confirmation=True
        ))

        self.register(Tool(
            name="get_alert_history",
            description="Récupère l'historique des alertes",
            category=ToolCategory.ALERTS,
            parameters=[
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période (ex: '24h', '7d')",
                    default="24h"
                ),
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Filtrer par équipement",
                    required=False
                ),
                ToolParameter(
                    name="group_by",
                    type="string",
                    description="Regrouper par",
                    required=False,
                    enum=["severity", "equipment", "type", "hour"]
                )
            ]
        ))

        # =======================================================================
        # PRODUCTION TOOLS
        # =======================================================================

        self.register(Tool(
            name="get_production_summary",
            description="Récupère le résumé de production",
            category=ToolCategory.PRODUCTION,
            parameters=[
                ToolParameter(
                    name="production_line",
                    type="string",
                    description="Ligne de production",
                    required=False
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période",
                    default="today"
                ),
                ToolParameter(
                    name="include_oee_breakdown",
                    type="boolean",
                    description="Inclure le détail OEE",
                    default=True
                )
            ]
        ))

        self.register(Tool(
            name="get_oee_analysis",
            description="Analyse détaillée de l'OEE (TRS)",
            category=ToolCategory.PRODUCTION,
            parameters=[
                ToolParameter(
                    name="production_line",
                    type="string",
                    description="Ligne de production",
                    required=False
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période d'analyse",
                    default="24h"
                ),
                ToolParameter(
                    name="compare_with",
                    type="string",
                    description="Période de comparaison",
                    required=False,
                    enum=["previous_period", "same_period_last_week", "same_period_last_month"]
                )
            ]
        ))

        self.register(Tool(
            name="get_downtime_analysis",
            description="Analyse des temps d'arrêt",
            category=ToolCategory.PRODUCTION,
            parameters=[
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période d'analyse",
                    default="7d"
                ),
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Filtrer par équipement",
                    required=False
                ),
                ToolParameter(
                    name="group_by",
                    type="string",
                    description="Regrouper par",
                    enum=["cause", "equipment", "shift", "day"],
                    default="cause"
                )
            ]
        ))

        # =======================================================================
        # MAINTENANCE TOOLS
        # =======================================================================

        self.register(Tool(
            name="get_maintenance_schedule",
            description="Récupère le planning de maintenance",
            category=ToolCategory.MAINTENANCE,
            parameters=[
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Filtrer par équipement",
                    required=False
                ),
                ToolParameter(
                    name="time_horizon",
                    type="string",
                    description="Horizon temporel",
                    default="30d"
                ),
                ToolParameter(
                    name="maintenance_type",
                    type="string",
                    description="Type de maintenance",
                    required=False,
                    enum=["preventive", "predictive", "corrective"]
                )
            ]
        ))

        self.register(Tool(
            name="get_predictive_insights",
            description="Récupère les insights de maintenance prédictive",
            category=ToolCategory.MAINTENANCE,
            parameters=[
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Identifiant de l'équipement"
                ),
                ToolParameter(
                    name="include_rul",
                    type="boolean",
                    description="Inclure la durée de vie résiduelle (RUL)",
                    default=True
                ),
                ToolParameter(
                    name="include_anomalies",
                    type="boolean",
                    description="Inclure les anomalies détectées",
                    default=True
                )
            ]
        ))

        self.register(Tool(
            name="create_maintenance_request",
            description="Crée une demande de maintenance",
            category=ToolCategory.MAINTENANCE,
            parameters=[
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Équipement concerné"
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="Priorité",
                    enum=["low", "medium", "high", "critical"],
                    default="medium"
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="Description du problème"
                ),
                ToolParameter(
                    name="suggested_action",
                    type="string",
                    description="Action suggérée",
                    required=False
                )
            ],
            requires_confirmation=True
        ))

        # =======================================================================
        # ANALYSIS TOOLS
        # =======================================================================

        self.register(Tool(
            name="analyze_root_cause",
            description="Lance une analyse de cause racine pour un incident",
            category=ToolCategory.ANALYSIS,
            parameters=[
                ToolParameter(
                    name="incident_id",
                    type="string",
                    description="Identifiant de l'incident",
                    required=False
                ),
                ToolParameter(
                    name="equipment_id",
                    type="string",
                    description="Équipement concerné",
                    required=False
                ),
                ToolParameter(
                    name="symptom",
                    type="string",
                    description="Symptôme observé",
                    required=False
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période à analyser",
                    default="1h"
                )
            ]
        ))

        self.register(Tool(
            name="correlate_events",
            description="Corrèle les événements pour identifier des patterns",
            category=ToolCategory.ANALYSIS,
            parameters=[
                ToolParameter(
                    name="event_types",
                    type="array",
                    description="Types d'événements à corréler",
                    items={"type": "string", "enum": [
                        "alert", "metric_anomaly", "downtime", "maintenance", "production_issue"
                    ]}
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période d'analyse",
                    default="7d"
                ),
                ToolParameter(
                    name="equipment_scope",
                    type="array",
                    description="Équipements à inclure",
                    required=False,
                    items={"type": "string"}
                )
            ]
        ))

        self.register(Tool(
            name="generate_report",
            description="Génère un rapport d'analyse",
            category=ToolCategory.ANALYSIS,
            parameters=[
                ToolParameter(
                    name="report_type",
                    type="string",
                    description="Type de rapport",
                    enum=["daily_summary", "oee_analysis", "maintenance_status", "alert_summary", "trend_analysis"]
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période du rapport",
                    default="24h"
                ),
                ToolParameter(
                    name="equipment_scope",
                    type="array",
                    description="Équipements à inclure",
                    required=False,
                    items={"type": "string"}
                ),
                ToolParameter(
                    name="format",
                    type="string",
                    description="Format de sortie",
                    enum=["summary", "detailed", "executive"],
                    default="summary"
                )
            ]
        ))

        # =======================================================================
        # SYSTEM TOOLS
        # =======================================================================

        self.register(Tool(
            name="search_logs",
            description="Recherche dans les logs système et applicatifs",
            category=ToolCategory.SYSTEM,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Requête de recherche"
                ),
                ToolParameter(
                    name="time_range",
                    type="string",
                    description="Période",
                    default="1h"
                ),
                ToolParameter(
                    name="source",
                    type="string",
                    description="Source des logs",
                    required=False,
                    enum=["application", "system", "scada", "plc", "all"]
                ),
                ToolParameter(
                    name="level",
                    type="string",
                    description="Niveau de log minimum",
                    required=False,
                    enum=["debug", "info", "warning", "error", "critical"]
                ),
                ToolParameter(
                    name="limit",
                    type="number",
                    description="Nombre max de résultats",
                    default=50
                )
            ]
        ))

        self.register(Tool(
            name="get_system_health",
            description="Récupère l'état de santé de la plateforme SYNAPSIX",
            category=ToolCategory.SYSTEM,
            parameters=[
                ToolParameter(
                    name="include_components",
                    type="boolean",
                    description="Inclure le statut de chaque composant",
                    default=True
                )
            ]
        ))

    def register(self, tool: Tool, handler: Optional[Callable] = None) -> None:
        """
        Register a tool.

        Args:
            tool: Tool definition
            handler: Optional handler function
        """
        self._tools[tool.name] = tool
        if handler:
            self._handlers[tool.name] = handler
        elif tool.handler:
            self._handlers[tool.name] = tool.handler

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(
        self,
        category: Optional[ToolCategory] = None
    ) -> List[Tool]:
        """
        List available tools.

        Args:
            category: Filter by category

        Returns:
            List of tools
        """
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return tools

    def get_function_schemas(
        self,
        categories: Optional[List[ToolCategory]] = None,
        tool_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get function schemas for LLM function calling.

        Args:
            categories: Filter by categories
            tool_names: Specific tools to include

        Returns:
            List of function schemas
        """
        tools = self._tools.values()

        if tool_names:
            tools = [t for t in tools if t.name in tool_names]
        elif categories:
            tools = [t for t in tools if t.category in categories]

        return [t.to_function_schema() for t in tools]

    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            context: Execution context

        Returns:
            Tool execution result
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }

        handler = self._handlers.get(tool_name)
        if not handler:
            # Return mock data for demo
            return self._mock_tool_response(tool_name, arguments)

        try:
            if tool.is_async:
                result = await handler(arguments, context)
            else:
                result = handler(arguments, context)

            return {
                "success": True,
                "data": result,
                "tool": tool_name
            }

        except Exception as e:
            logger.error(f"Tool execution error for {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

    def _mock_tool_response(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate mock response for demo purposes."""
        # This would be replaced with actual integrations
        return {
            "success": True,
            "data": {
                "message": f"Tool '{tool_name}' executed with arguments: {arguments}",
                "mock": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            "tool": tool_name
        }


class ToolExecutor:
    """
    Manages tool execution and result formatting.

    Features:
    - Confirmation handling for dangerous operations
    - Result caching
    - Execution history
    """

    def __init__(self, registry: ToolRegistry):
        """Initialize the tool executor."""
        self.registry = registry
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._max_history = 100

    async def execute_with_confirmation(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a tool with confirmation handling.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            context: Execution context
            confirmed: Whether the action is confirmed

        Returns:
            Execution result or confirmation request
        """
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}

        if tool.requires_confirmation and not confirmed:
            confirmation_id = f"{tool_name}_{datetime.utcnow().timestamp()}"
            self._pending_confirmations[confirmation_id] = {
                "tool_name": tool_name,
                "arguments": arguments,
                "context": context,
                "created_at": datetime.utcnow()
            }

            return {
                "requires_confirmation": True,
                "confirmation_id": confirmation_id,
                "tool": tool_name,
                "message": f"Cette action nécessite une confirmation. Voulez-vous vraiment exécuter '{tool_name}'?"
            }

        result = await self.registry.execute(tool_name, arguments, context)

        # Log execution
        self._log_execution(tool_name, arguments, result)

        return result

    def confirm(self, confirmation_id: str) -> Optional[Dict[str, Any]]:
        """Get pending confirmation details."""
        return self._pending_confirmations.get(confirmation_id)

    async def execute_confirmed(self, confirmation_id: str) -> Dict[str, Any]:
        """Execute a confirmed action."""
        pending = self._pending_confirmations.pop(confirmation_id, None)
        if not pending:
            return {"success": False, "error": "Confirmation expired or not found"}

        return await self.registry.execute(
            pending["tool_name"],
            pending["arguments"],
            pending["context"]
        )

    def _log_execution(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Log tool execution."""
        self._execution_history.append({
            "tool": tool_name,
            "arguments": arguments,
            "success": result.get("success", False),
            "timestamp": datetime.utcnow().isoformat()
        })

        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self._execution_history[-limit:]


# Global instances
_tool_registry: Optional[ToolRegistry] = None
_tool_executor: Optional[ToolExecutor] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create the global tool registry."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def get_tool_executor() -> ToolExecutor:
    """Get or create the global tool executor."""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutor(get_tool_registry())
    return _tool_executor
