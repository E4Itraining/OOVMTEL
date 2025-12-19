"""
LLM Integration Module - Abstraction layer for AI/LLM providers.

This module provides a unified interface for integrating various LLM providers
(Mistral, Claude, OpenAI, etc.) into the SYNAPSIX platform.

Features:
- Provider-agnostic interface (BaseLLMProvider)
- Mistral AI integration (MistralProvider)
- Industrial context prompts for OT/IT observability
- Async support for high-performance inference
- Streaming responses for real-time interaction
- Token usage tracking and cost estimation
- Adaptive personas for different user roles
- Advanced conversational memory management
- Function calling / tools for platform integration
- Enriched response templates
- User feedback collection and analysis
"""

from .base import (
    BaseLLMProvider,
    LLMResponse,
    LLMMessage,
    LLMConfig,
    ProviderType,
    LLMCapability,
    MessageRole,
)
from .mistral_client import MistralProvider
from .prompts import IndustrialPrompts, PromptTemplate, PromptLanguage
from .config import LLMSettings, get_llm_settings
from .nlp_integration import LLMEnhancedNLP, get_llm_nlp

# Enhanced modules
from .personas import (
    Persona,
    PersonaType,
    PersonaManager,
    get_persona_manager,
)
from .memory import (
    MemoryEntry,
    MemoryType,
    SessionMemory,
    LongTermMemory,
    MemoryManager,
    get_memory_manager,
    ConversationTurn,
    ConversationSummary,
)
from .tools import (
    Tool,
    ToolParameter,
    ToolCategory,
    ToolRegistry,
    ToolExecutor,
    get_tool_registry,
    get_tool_executor,
)
from .response_templates import (
    ResponseTemplates,
    ResponseFormatter,
    TemplateType,
    StatusIndicator,
    MetricCard,
    ActionItem,
)
from .feedback import (
    FeedbackEntry,
    FeedbackType,
    FeedbackSentiment,
    FeedbackStats,
    FeedbackCollector,
    FeedbackAnalyzer,
    FeedbackReporter,
    get_feedback_collector,
    get_feedback_analyzer,
)
from .enhanced_assistant import (
    EnhancedAssistant,
    get_enhanced_assistant,
)

__all__ = [
    # Base classes
    "BaseLLMProvider",
    "LLMResponse",
    "LLMMessage",
    "LLMConfig",
    "ProviderType",
    "LLMCapability",
    "MessageRole",
    # Providers
    "MistralProvider",
    # NLP Integration
    "LLMEnhancedNLP",
    "get_llm_nlp",
    # Prompts
    "IndustrialPrompts",
    "PromptTemplate",
    "PromptLanguage",
    # Config
    "LLMSettings",
    "get_llm_settings",
    # Personas
    "Persona",
    "PersonaType",
    "PersonaManager",
    "get_persona_manager",
    # Memory
    "MemoryEntry",
    "MemoryType",
    "SessionMemory",
    "LongTermMemory",
    "MemoryManager",
    "get_memory_manager",
    "ConversationTurn",
    "ConversationSummary",
    # Tools
    "Tool",
    "ToolParameter",
    "ToolCategory",
    "ToolRegistry",
    "ToolExecutor",
    "get_tool_registry",
    "get_tool_executor",
    # Response Templates
    "ResponseTemplates",
    "ResponseFormatter",
    "TemplateType",
    "StatusIndicator",
    "MetricCard",
    "ActionItem",
    # Feedback
    "FeedbackEntry",
    "FeedbackType",
    "FeedbackSentiment",
    "FeedbackStats",
    "FeedbackCollector",
    "FeedbackAnalyzer",
    "FeedbackReporter",
    "get_feedback_collector",
    "get_feedback_analyzer",
    # Enhanced Assistant
    "EnhancedAssistant",
    "get_enhanced_assistant",
]
