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
"""

from .base import (
    BaseLLMProvider,
    LLMResponse,
    LLMMessage,
    LLMConfig,
    ProviderType,
    LLMCapability,
)
from .mistral_client import MistralProvider
from .prompts import IndustrialPrompts, PromptTemplate
from .config import LLMSettings, get_llm_settings

__all__ = [
    # Base classes
    "BaseLLMProvider",
    "LLMResponse",
    "LLMMessage",
    "LLMConfig",
    "ProviderType",
    "LLMCapability",
    # Providers
    "MistralProvider",
    # Prompts
    "IndustrialPrompts",
    "PromptTemplate",
    # Config
    "LLMSettings",
    "get_llm_settings",
]
