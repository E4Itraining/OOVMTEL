"""
NLP-LLM Integration Module.

Provides enhanced NLP capabilities by combining rule-based extraction
with LLM-powered understanding and generation.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseLLMProvider, LLMMessage, LLMResponse, MessageRole, LLMConfig, ProviderType
from .mistral_client import MistralProvider
from .prompts import IndustrialPrompts
from .config import get_llm_settings, LLMSettings

logger = logging.getLogger(__name__)


class LLMEnhancedNLP:
    """
    LLM-enhanced NLP processor for industrial observability.

    Combines rule-based entity extraction with LLM-powered:
    - Natural language understanding
    - Response generation
    - Context-aware analysis
    - Multi-turn conversation support
    """

    def __init__(
        self,
        settings: Optional[LLMSettings] = None,
        fallback_enabled: bool = True
    ):
        """
        Initialize the LLM-enhanced NLP processor.

        Args:
            settings: LLM settings (uses defaults if not provided)
            fallback_enabled: Enable rule-based fallback if LLM unavailable
        """
        self.settings = settings or get_llm_settings()
        self.fallback_enabled = fallback_enabled
        self._provider: Optional[BaseLLMProvider] = None
        self._initialized = False

        # Conversation history per session
        self._conversations: Dict[str, List[LLMMessage]] = {}
        self._max_history = 10  # Keep last N messages per session

    async def initialize(self) -> bool:
        """
        Initialize the LLM provider.

        Returns:
            True if LLM is available, False if falling back to rules
        """
        if self._initialized:
            return self._provider is not None

        if not self.settings.llm_enabled:
            logger.info("LLM disabled by configuration")
            self._initialized = True
            return False

        if not self.settings.is_configured():
            logger.warning("LLM not configured (missing API key)")
            self._initialized = True
            return False

        try:
            # Create provider based on settings
            config = self.settings.get_active_config()

            if config.provider == ProviderType.MISTRAL:
                self._provider = MistralProvider(config)
            else:
                logger.warning(f"Provider {config.provider} not yet implemented")
                self._initialized = True
                return False

            # Initialize provider
            success = await self._provider.initialize()
            if success:
                logger.info(f"LLM provider initialized: {config.provider.value}/{config.model}")
            else:
                logger.warning("LLM provider initialization failed")
                self._provider = None

            self._initialized = True
            return success

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self._initialized = True
            return False

    @property
    def is_llm_available(self) -> bool:
        """Check if LLM is available for use."""
        return self._provider is not None

    async def generate_response(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        metrics_context: Dict[str, Any],
        language: str = "fr",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using LLM with industrial context.

        Args:
            query: User's natural language query
            intent: Detected intent (from rule-based extraction)
            entities: Extracted entities (equipment, metrics, time)
            metrics_context: Current metrics data
            language: Response language (fr/en)
            session_id: Session ID for conversation history

        Returns:
            Dictionary with response content and metadata
        """
        if not await self.initialize():
            return self._create_fallback_response(query, intent, entities, language)

        try:
            # Get system prompt
            system_prompt = IndustrialPrompts.get_system_prompt(language)

            # Format metrics context
            formatted_context = IndustrialPrompts.format_metrics_context(metrics_context)

            # Get conversation history
            history = self._get_history(session_id) if session_id else []

            # Build intent-specific prompt
            user_prompt = self._build_user_prompt(
                query=query,
                intent=intent,
                entities=entities,
                metrics_context=formatted_context,
                language=language
            )

            # Prepare messages
            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt)
            ]
            messages.extend(history)
            messages.append(LLMMessage(role=MessageRole.USER, content=user_prompt))

            # Generate response
            response = await self._provider.generate(messages)

            # Update conversation history
            if session_id:
                self._update_history(session_id, query, response.content)

            return {
                "content": response.content,
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.total_tokens,
                "latency_ms": response.latency_ms,
                "llm_enhanced": True,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            if self.fallback_enabled:
                return self._create_fallback_response(query, intent, entities, language)
            raise

    async def generate_streaming_response(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        metrics_context: Dict[str, Any],
        language: str = "fr"
    ):
        """
        Generate a streaming response for real-time display.

        Yields:
            String chunks of the response
        """
        if not await self.initialize():
            # Fallback doesn't support streaming, yield full response
            fallback = self._create_fallback_response(query, intent, entities, language)
            yield fallback["content"]
            return

        try:
            system_prompt = IndustrialPrompts.get_system_prompt(language)
            formatted_context = IndustrialPrompts.format_metrics_context(metrics_context)

            user_prompt = self._build_user_prompt(
                query=query,
                intent=intent,
                entities=entities,
                metrics_context=formatted_context,
                language=language
            )

            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt),
                LLMMessage(role=MessageRole.USER, content=user_prompt)
            ]

            async for chunk in self._provider.generate_stream(messages):
                yield chunk

        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            if self.fallback_enabled:
                fallback = self._create_fallback_response(query, intent, entities, language)
                yield fallback["content"]
            else:
                raise

    async def analyze_root_cause(
        self,
        incident_title: str,
        incident_description: str,
        severity: str,
        detected_at: str,
        metrics_context: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Perform LLM-enhanced root cause analysis.

        Returns:
            Dictionary with RCA results
        """
        if not await self.initialize():
            return {"error": "LLM not available", "llm_enhanced": False}

        try:
            system_prompt = IndustrialPrompts.get_system_prompt(language)
            formatted_context = IndustrialPrompts.format_metrics_context(metrics_context)
            formatted_timeline = "\n".join([
                f"- {e.get('time', 'N/A')}: {e.get('event', 'N/A')}"
                for e in timeline
            ])

            rca_prompt = IndustrialPrompts.get_rca_prompt(
                incident_title=incident_title,
                incident_description=incident_description,
                severity=severity,
                detected_at=detected_at,
                metrics_context=formatted_context,
                timeline=formatted_timeline,
                language=language
            )

            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt),
                LLMMessage(role=MessageRole.USER, content=rca_prompt)
            ]

            response = await self._provider.generate(messages)

            return {
                "analysis": response.content,
                "model": response.model,
                "tokens_used": response.total_tokens,
                "latency_ms": response.latency_ms,
                "llm_enhanced": True
            }

        except Exception as e:
            logger.error(f"RCA LLM error: {e}")
            return {"error": str(e), "llm_enhanced": False}

    async def analyze_predictive(
        self,
        equipment_name: str,
        equipment_type: str,
        current_metrics: Dict[str, Any],
        historical_metrics: List[Dict[str, Any]],
        maintenance_history: List[Dict[str, Any]],
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Perform LLM-enhanced predictive maintenance analysis.

        Returns:
            Dictionary with predictive analysis results
        """
        if not await self.initialize():
            return {"error": "LLM not available", "llm_enhanced": False}

        try:
            system_prompt = IndustrialPrompts.get_system_prompt(language)

            # Format contexts
            current_str = "\n".join([f"- {k}: {v}" for k, v in current_metrics.items()])
            historical_str = "\n".join([
                f"- {h.get('date', 'N/A')}: {h.get('metrics', {})}"
                for h in historical_metrics[-10:]  # Last 10 entries
            ])
            maintenance_str = "\n".join([
                f"- {m.get('date', 'N/A')}: {m.get('action', 'N/A')}"
                for m in maintenance_history[-5:]  # Last 5 entries
            ])

            predictive_prompt = IndustrialPrompts.get_predictive_prompt(
                equipment_name=equipment_name,
                equipment_type=equipment_type,
                current_metrics=current_str,
                historical_metrics=historical_str,
                maintenance_history=maintenance_str,
                language=language
            )

            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt),
                LLMMessage(role=MessageRole.USER, content=predictive_prompt)
            ]

            response = await self._provider.generate(messages)

            return {
                "analysis": response.content,
                "model": response.model,
                "tokens_used": response.total_tokens,
                "latency_ms": response.latency_ms,
                "llm_enhanced": True
            }

        except Exception as e:
            logger.error(f"Predictive LLM error: {e}")
            return {"error": str(e), "llm_enhanced": False}

    def _build_user_prompt(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        metrics_context: str,
        language: str
    ) -> str:
        """Build the user prompt based on intent."""
        # Add entity context
        entity_context = ""
        if entities.get("equipment"):
            entity_context += f"\nÉquipements mentionnés: {', '.join(entities['equipment'])}"
        if entities.get("metrics"):
            entity_context += f"\nMétriques demandées: {', '.join(entities['metrics'])}"
        if entities.get("time_range"):
            entity_context += f"\nPériode: {entities['time_range']}"

        # Build intent-specific prompt
        if intent == "TROUBLESHOOTING":
            base = IndustrialPrompts.TROUBLESHOOTING_PROMPT_FR if language == "fr" else IndustrialPrompts.TROUBLESHOOTING_PROMPT_EN
            return base.format(
                query=query,
                equipment_context=entity_context,
                metrics_context=metrics_context,
                alarms_context="Voir section alarmes dans les métriques"
            )
        elif intent in ["METRICS_QUERY", "SUMMARY"]:
            base = IndustrialPrompts.METRICS_QUERY_PROMPT_FR if language == "fr" else IndustrialPrompts.METRICS_QUERY_PROMPT_EN
            return base.format(
                query=query,
                metrics_context=metrics_context
            )
        else:
            # Generic prompt
            return f"""Question: {query}
{entity_context}

Contexte actuel:
{metrics_context}

Réponds de manière concise et professionnelle."""

    def _create_fallback_response(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Create a fallback response when LLM is unavailable."""
        if language == "fr":
            content = f"Je comprends que vous cherchez des informations sur {intent.lower().replace('_', ' ')}. "
            if entities.get("equipment"):
                content += f"Équipements concernés: {', '.join(entities['equipment'])}. "
            if entities.get("metrics"):
                content += f"Métriques demandées: {', '.join(entities['metrics'])}. "
            content += "Consultez le tableau de bord pour les données en temps réel."
        else:
            content = f"I understand you're looking for information about {intent.lower().replace('_', ' ')}. "
            if entities.get("equipment"):
                content += f"Equipment involved: {', '.join(entities['equipment'])}. "
            if entities.get("metrics"):
                content += f"Requested metrics: {', '.join(entities['metrics'])}. "
            content += "Check the dashboard for real-time data."

        return {
            "content": content,
            "model": "rule-based",
            "provider": "fallback",
            "tokens_used": 0,
            "latency_ms": 0,
            "llm_enhanced": False
        }

    def _get_history(self, session_id: str) -> List[LLMMessage]:
        """Get conversation history for a session."""
        return self._conversations.get(session_id, [])

    def _update_history(self, session_id: str, user_query: str, assistant_response: str):
        """Update conversation history."""
        if session_id not in self._conversations:
            self._conversations[session_id] = []

        history = self._conversations[session_id]
        history.append(LLMMessage(role=MessageRole.USER, content=user_query))
        history.append(LLMMessage(role=MessageRole.ASSISTANT, content=assistant_response))

        # Trim history if too long
        if len(history) > self._max_history * 2:
            self._conversations[session_id] = history[-self._max_history * 2:]

    def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self._conversations:
            del self._conversations[session_id]

    async def health_check(self) -> Dict[str, Any]:
        """Check LLM provider health."""
        if not self._provider:
            return {
                "status": "unavailable",
                "llm_enabled": self.settings.llm_enabled,
                "configured": self.settings.is_configured(),
                "fallback_available": self.fallback_enabled
            }

        try:
            health = await self._provider.health_check()
            health["fallback_available"] = self.fallback_enabled
            return health
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback_available": self.fallback_enabled
            }

    async def close(self):
        """Clean up resources."""
        if self._provider:
            await self._provider.close()
            self._provider = None
        self._conversations.clear()


# Singleton instance
_llm_nlp: Optional[LLMEnhancedNLP] = None


async def get_llm_nlp() -> LLMEnhancedNLP:
    """Get or create the LLM-enhanced NLP singleton."""
    global _llm_nlp
    if _llm_nlp is None:
        _llm_nlp = LLMEnhancedNLP()
        await _llm_nlp.initialize()
    return _llm_nlp
