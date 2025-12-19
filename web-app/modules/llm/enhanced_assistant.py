"""
Enhanced Assistant Module.

Provides a fully-featured AI assistant that integrates all advanced capabilities:
- Persona-based communication
- Advanced memory management
- Function calling / tools
- Enriched response templates
- User feedback collection
"""

import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from .base import BaseLLMProvider, LLMMessage, MessageRole, LLMConfig, ProviderType
from .mistral_client import MistralProvider
from .prompts import IndustrialPrompts
from .config import get_llm_settings, LLMSettings
from .personas import PersonaType, PersonaManager, Persona, get_persona_manager
from .memory import MemoryManager, SessionMemory, get_memory_manager
from .tools import ToolRegistry, ToolExecutor, ToolCategory, get_tool_registry, get_tool_executor
from .response_templates import ResponseTemplates, ResponseFormatter, MetricCard, StatusIndicator
from .feedback import FeedbackCollector, get_feedback_collector

logger = logging.getLogger(__name__)


class EnhancedAssistant:
    """
    Enhanced AI assistant with full feature integration.

    Features:
    - Adaptive personas for different user roles
    - Sophisticated memory management with summarization
    - Function calling for platform integration
    - Structured response templates
    - Feedback collection and learning
    - Multi-language support (FR/EN)
    """

    def __init__(
        self,
        settings: Optional[LLMSettings] = None,
        default_persona: PersonaType = PersonaType.DEFAULT,
        enable_tools: bool = True,
        enable_feedback: bool = True
    ):
        """
        Initialize the enhanced assistant.

        Args:
            settings: LLM configuration settings
            default_persona: Default persona to use
            enable_tools: Enable function calling
            enable_feedback: Enable feedback collection
        """
        self.settings = settings or get_llm_settings()
        self.default_persona = default_persona
        self.enable_tools = enable_tools
        self.enable_feedback = enable_feedback

        # Core components
        self._provider: Optional[BaseLLMProvider] = None
        self._persona_manager = get_persona_manager()
        self._memory_manager = get_memory_manager()
        self._tool_registry = get_tool_registry() if enable_tools else None
        self._tool_executor = get_tool_executor() if enable_tools else None
        self._feedback_collector = get_feedback_collector() if enable_feedback else None

        # State
        self._initialized = False
        self._current_persona = self._persona_manager.get_persona(default_persona)

    async def initialize(self) -> bool:
        """
        Initialize the assistant and LLM provider.

        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True

        if not self.settings.llm_enabled:
            logger.info("LLM disabled by configuration")
            self._initialized = True
            return False

        if not self.settings.is_configured():
            logger.warning("LLM not configured (missing API key)")
            self._initialized = True
            return False

        try:
            config = self.settings.get_active_config()

            if config.provider == ProviderType.MISTRAL:
                self._provider = MistralProvider(config)
            else:
                logger.warning(f"Provider {config.provider} not yet implemented")
                self._initialized = True
                return False

            success = await self._provider.initialize()
            if success:
                logger.info(f"Enhanced assistant initialized with {config.provider.value}/{config.model}")
            else:
                logger.warning("LLM provider initialization failed")
                self._provider = None

            self._initialized = True
            return success

        except Exception as e:
            logger.error(f"Failed to initialize enhanced assistant: {e}")
            self._initialized = True
            return False

    @property
    def is_available(self) -> bool:
        """Check if the assistant is available."""
        return self._provider is not None

    async def chat(
        self,
        query: str,
        session_id: str,
        language: str = "fr",
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        metrics_context: Optional[Dict[str, Any]] = None,
        persona_override: Optional[PersonaType] = None,
        use_tools: bool = True,
        collect_feedback: bool = True
    ) -> Dict[str, Any]:
        """
        Process a chat message with full feature integration.

        Args:
            query: User's message
            session_id: Session identifier
            language: Response language (fr/en)
            intent: Pre-detected intent
            entities: Pre-extracted entities
            metrics_context: Current metrics data
            persona_override: Override the default persona
            use_tools: Enable tool usage for this query
            collect_feedback: Enable feedback collection for this response

        Returns:
            Complete response with metadata
        """
        if not await self.initialize():
            return self._create_fallback_response(query, language)

        start_time = datetime.utcnow()
        message_id = f"{session_id}_{start_time.timestamp()}"

        try:
            # Get session memory
            session = self._memory_manager.get_session(session_id)
            session.language = language

            # Determine persona
            persona = self._get_persona(query, language, persona_override)

            # Build system prompt with persona
            system_prompt = self._build_system_prompt(persona, language)

            # Get conversation context
            context = session.get_context(max_turns=5)

            # Format metrics context
            formatted_metrics = ""
            if metrics_context:
                formatted_metrics = IndustrialPrompts.format_metrics_context(metrics_context)

            # Build user prompt
            user_prompt = self._build_user_prompt(
                query=query,
                intent=intent,
                entities=entities,
                metrics_context=formatted_metrics,
                entity_context=session.get_entity_context(),
                language=language
            )

            # Prepare messages
            messages = [LLMMessage(role=MessageRole.SYSTEM, content=system_prompt)]

            # Add summarized history if available
            if session._summaries:
                summary_text = self._format_summaries(session._summaries[-2:], language)
                messages.append(LLMMessage(role=MessageRole.SYSTEM, content=summary_text))

            # Add recent conversation
            for turn in context:
                messages.append(LLMMessage(
                    role=MessageRole.USER if turn["role"] == "user" else MessageRole.ASSISTANT,
                    content=turn["content"]
                ))

            messages.append(LLMMessage(role=MessageRole.USER, content=user_prompt))

            # Get available tools if enabled
            tools = None
            if use_tools and self._tool_registry:
                tools = self._get_relevant_tools(intent)

            # Generate response
            response = await self._provider.generate(messages, tools=tools)

            # Format response with template if appropriate
            formatted_content = self._format_response(
                content=response.content,
                intent=intent,
                persona=persona,
                language=language
            )

            # Update session memory
            session.add_turn(
                role="user",
                content=query,
                intent=intent,
                entities=entities
            )
            session.add_turn(
                role="assistant",
                content=response.content,
                intent=intent
            )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Build response
            result = {
                "message_id": message_id,
                "content": formatted_content,
                "raw_content": response.content,
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.total_tokens,
                "latency_ms": response.latency_ms,
                "processing_time_ms": processing_time,
                "persona": persona.name,
                "language": language,
                "intent": intent,
                "llm_enhanced": True,
                "tools_used": [],
                "suggestions": self._generate_suggestions(intent, entities, language),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Handle tool calls if present
            if response.tool_calls and self._tool_executor:
                result["tools_used"] = await self._execute_tools(response.tool_calls, session_id)

            return result

        except Exception as e:
            logger.error(f"Enhanced assistant error: {e}")
            return self._create_fallback_response(query, language)

    async def chat_stream(
        self,
        query: str,
        session_id: str,
        language: str = "fr",
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        metrics_context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat response.

        Yields:
            Response content chunks
        """
        if not await self.initialize():
            yield self._create_fallback_response(query, language)["content"]
            return

        try:
            session = self._memory_manager.get_session(session_id)
            persona = self._get_persona(query, language, None)
            system_prompt = self._build_system_prompt(persona, language)

            formatted_metrics = ""
            if metrics_context:
                formatted_metrics = IndustrialPrompts.format_metrics_context(metrics_context)

            user_prompt = self._build_user_prompt(
                query=query,
                intent=intent,
                entities=entities,
                metrics_context=formatted_metrics,
                entity_context=session.get_entity_context(),
                language=language
            )

            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt),
                LLMMessage(role=MessageRole.USER, content=user_prompt)
            ]

            full_response = ""
            async for chunk in self._provider.generate_stream(messages):
                full_response += chunk
                yield chunk

            # Update memory after streaming completes
            session.add_turn("user", query, intent, entities)
            session.add_turn("assistant", full_response, intent)

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield self._create_fallback_response(query, language)["content"]

    def submit_feedback(
        self,
        session_id: str,
        message_id: str,
        is_positive: bool,
        query: Optional[str] = None,
        response: Optional[str] = None,
        intent: Optional[str] = None
    ) -> Optional[str]:
        """
        Submit feedback for a response.

        Returns:
            Feedback entry ID if collected
        """
        if not self._feedback_collector:
            return None

        return self._feedback_collector.submit_rating(
            session_id=session_id,
            message_id=message_id,
            is_positive=is_positive,
            query=query,
            response=response,
            intent=intent
        )

    def set_persona(self, persona_type: PersonaType) -> Persona:
        """Set the current persona."""
        self._current_persona = self._persona_manager.get_persona(persona_type)
        return self._current_persona

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session."""
        session = self._memory_manager.get_session(session_id)
        return session.get_stats()

    def clear_session(self, session_id: str) -> None:
        """Clear a session's memory."""
        session = self._memory_manager.get_session(session_id)
        session.clear()

    # ==========================================================================
    # PRIVATE METHODS
    # ==========================================================================

    def _get_persona(
        self,
        query: str,
        language: str,
        override: Optional[PersonaType]
    ) -> Persona:
        """Determine the appropriate persona."""
        if override:
            return self._persona_manager.get_persona(override)

        # Auto-detect based on query
        detected = self._persona_manager.detect_persona(query, language)
        if detected.type != PersonaType.DEFAULT:
            return detected

        return self._current_persona

    def _build_system_prompt(self, persona: Persona, language: str) -> str:
        """Build the complete system prompt."""
        base_prompt = IndustrialPrompts.get_system_prompt(language)
        persona_instructions = persona.get_style_instructions(language)

        return f"{base_prompt}\n{persona_instructions}"

    def _build_user_prompt(
        self,
        query: str,
        intent: Optional[str],
        entities: Optional[Dict[str, Any]],
        metrics_context: str,
        entity_context: str,
        language: str
    ) -> str:
        """Build the user prompt with all context."""
        parts = []

        # Add entity context from memory
        if entity_context:
            if language == "fr":
                parts.append(f"Contexte de la conversation:\n{entity_context}")
            else:
                parts.append(f"Conversation context:\n{entity_context}")

        # Add current entities
        if entities:
            entity_str = self._format_entities(entities, language)
            if entity_str:
                parts.append(entity_str)

        # Add metrics context
        if metrics_context:
            if language == "fr":
                parts.append(f"Données actuelles:\n{metrics_context}")
            else:
                parts.append(f"Current data:\n{metrics_context}")

        # Add the query
        if language == "fr":
            parts.append(f"Question: {query}")
        else:
            parts.append(f"Question: {query}")

        return "\n\n".join(parts)

    def _format_entities(self, entities: Dict[str, Any], language: str) -> str:
        """Format extracted entities."""
        lines = []

        if entities.get("equipment"):
            label = "Équipements" if language == "fr" else "Equipment"
            equipment = entities["equipment"]
            if isinstance(equipment, list):
                lines.append(f"{label}: {', '.join(equipment)}")
            else:
                lines.append(f"{label}: {equipment}")

        if entities.get("metrics"):
            label = "Métriques" if language == "fr" else "Metrics"
            metrics = entities["metrics"]
            if isinstance(metrics, list):
                lines.append(f"{label}: {', '.join(metrics)}")
            else:
                lines.append(f"{label}: {metrics}")

        if entities.get("time_range"):
            label = "Période" if language == "fr" else "Time range"
            lines.append(f"{label}: {entities['time_range']}")

        return "\n".join(lines)

    def _format_summaries(
        self,
        summaries: List,
        language: str
    ) -> str:
        """Format conversation summaries for context."""
        if language == "fr":
            header = "Résumé de la conversation précédente:"
        else:
            header = "Previous conversation summary:"

        summary_lines = [header]
        for s in summaries:
            summary_lines.append(f"- {s.summary}")

        return "\n".join(summary_lines)

    def _format_response(
        self,
        content: str,
        intent: Optional[str],
        persona: Persona,
        language: str
    ) -> str:
        """Format the response based on intent and persona."""
        # Apply persona formatting
        formatted = self._persona_manager.format_response(content, persona, language)

        return formatted

    def _get_relevant_tools(self, intent: Optional[str]) -> Optional[List[Dict[str, Any]]]:
        """Get tools relevant to the current intent."""
        if not self._tool_registry:
            return None

        # Map intents to tool categories
        intent_to_categories = {
            "METRICS_QUERY": [ToolCategory.METRICS],
            "EQUIPMENT_STATUS": [ToolCategory.EQUIPMENT],
            "ALERT_STATUS": [ToolCategory.ALERTS],
            "TROUBLESHOOTING": [ToolCategory.EQUIPMENT, ToolCategory.ALERTS, ToolCategory.ANALYSIS],
            "PRODUCTION_STATUS": [ToolCategory.PRODUCTION],
            "ROOT_CAUSE": [ToolCategory.ANALYSIS],
            "PREDICTION": [ToolCategory.MAINTENANCE, ToolCategory.ANALYSIS]
        }

        categories = intent_to_categories.get(intent, None)
        return self._tool_registry.get_function_schemas(categories=categories)

    async def _execute_tools(
        self,
        tool_calls: List[Dict[str, Any]],
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tool calls."""
        results = []

        for call in tool_calls:
            tool_name = call.get("function", {}).get("name")
            arguments = call.get("function", {}).get("arguments", {})

            if tool_name:
                result = await self._tool_executor.execute_with_confirmation(
                    tool_name=tool_name,
                    arguments=arguments,
                    context={"session_id": session_id}
                )
                results.append({
                    "tool": tool_name,
                    "result": result
                })

        return results

    def _generate_suggestions(
        self,
        intent: Optional[str],
        entities: Optional[Dict[str, Any]],
        language: str
    ) -> List[str]:
        """Generate follow-up question suggestions."""
        suggestions = []

        # Intent-based suggestions
        intent_suggestions = {
            "fr": {
                "METRICS_QUERY": [
                    "Montre-moi l'évolution sur les dernières 24h",
                    "Compare avec la semaine dernière",
                    "Y a-t-il des anomalies détectées?"
                ],
                "EQUIPMENT_STATUS": [
                    "Quel est le score de santé de cet équipement?",
                    "Y a-t-il des maintenances prévues?",
                    "Montre-moi les alertes récentes"
                ],
                "ALERT_STATUS": [
                    "Quelle est la cause probable de cette alerte?",
                    "Quelles actions sont recommandées?",
                    "Y a-t-il des corrélations avec d'autres alertes?"
                ],
                "TROUBLESHOOTING": [
                    "Analyse la cause racine de ce problème",
                    "Montre-moi l'historique des incidents similaires",
                    "Quelles sont les actions correctives?"
                ]
            },
            "en": {
                "METRICS_QUERY": [
                    "Show me the trend over the last 24h",
                    "Compare with last week",
                    "Are there any anomalies detected?"
                ],
                "EQUIPMENT_STATUS": [
                    "What is the health score of this equipment?",
                    "Are there any scheduled maintenances?",
                    "Show me recent alerts"
                ],
                "ALERT_STATUS": [
                    "What is the probable cause of this alert?",
                    "What actions are recommended?",
                    "Are there correlations with other alerts?"
                ],
                "TROUBLESHOOTING": [
                    "Analyze the root cause of this issue",
                    "Show me history of similar incidents",
                    "What are the corrective actions?"
                ]
            }
        }

        lang_suggestions = intent_suggestions.get(language, intent_suggestions["fr"])
        if intent in lang_suggestions:
            suggestions = lang_suggestions[intent][:2]

        # Add equipment-specific suggestion
        if entities and entities.get("equipment") and language == "fr":
            equipment = entities["equipment"]
            if isinstance(equipment, list):
                equipment = equipment[0]
            suggestions.append(f"Montre-moi toutes les métriques de {equipment}")

        return suggestions

    def _create_fallback_response(self, query: str, language: str) -> Dict[str, Any]:
        """Create a fallback response when LLM is unavailable."""
        if language == "fr":
            content = (
                "Je suis actuellement en mode dégradé. "
                "Consultez le tableau de bord pour les données en temps réel."
            )
        else:
            content = (
                "I'm currently in degraded mode. "
                "Check the dashboard for real-time data."
            )

        return {
            "message_id": f"fallback_{datetime.utcnow().timestamp()}",
            "content": content,
            "raw_content": content,
            "model": "fallback",
            "provider": "rule-based",
            "tokens_used": 0,
            "latency_ms": 0,
            "processing_time_ms": 0,
            "persona": "default",
            "language": language,
            "llm_enhanced": False,
            "tools_used": [],
            "suggestions": [],
            "timestamp": datetime.utcnow().isoformat()
        }

    async def close(self):
        """Clean up resources."""
        if self._provider:
            await self._provider.close()
            self._provider = None


# Singleton instance
_enhanced_assistant: Optional[EnhancedAssistant] = None


async def get_enhanced_assistant() -> EnhancedAssistant:
    """Get or create the global enhanced assistant."""
    global _enhanced_assistant
    if _enhanced_assistant is None:
        _enhanced_assistant = EnhancedAssistant()
        await _enhanced_assistant.initialize()
    return _enhanced_assistant
