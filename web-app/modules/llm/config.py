"""
LLM Configuration Module.

Handles environment-based configuration for LLM providers with sensible defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from functools import lru_cache

from .base import ProviderType, LLMConfig


@dataclass
class MistralSettings:
    """Mistral-specific settings."""
    api_key: Optional[str] = None
    api_base: str = "https://api.mistral.ai/v1"
    model: str = "mistral-large-latest"
    temperature: float = 0.3  # Lower for more deterministic industrial responses
    max_tokens: int = 2048
    safe_prompt: bool = True

    # Available Mistral models
    AVAILABLE_MODELS: List[str] = field(default_factory=lambda: [
        "mistral-large-latest",       # Most capable, best for complex analysis
        "mistral-medium-latest",      # Balanced performance/cost
        "mistral-small-latest",       # Fast, cost-effective
        "codestral-latest",           # Optimized for code
        "mistral-embed",              # For embeddings
        "open-mistral-nemo",          # Open weight model
    ])

    @classmethod
    def from_env(cls) -> "MistralSettings":
        """Create settings from environment variables."""
        return cls(
            api_key=os.getenv("MISTRAL_API_KEY"),
            api_base=os.getenv("MISTRAL_API_BASE", "https://api.mistral.ai/v1"),
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            temperature=float(os.getenv("MISTRAL_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("MISTRAL_MAX_TOKENS", "2048")),
            safe_prompt=os.getenv("MISTRAL_SAFE_PROMPT", "true").lower() == "true",
        )

    def to_llm_config(self) -> LLMConfig:
        """Convert to LLMConfig."""
        return LLMConfig(
            provider=ProviderType.MISTRAL,
            api_key=self.api_key,
            api_base=self.api_base,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            safe_prompt=self.safe_prompt,
        )


@dataclass
class ClaudeSettings:
    """Claude/Anthropic-specific settings (for future integration)."""
    api_key: Optional[str] = None
    api_base: str = "https://api.anthropic.com/v1"
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.3
    max_tokens: int = 4096

    @classmethod
    def from_env(cls) -> "ClaudeSettings":
        """Create settings from environment variables."""
        return cls(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            api_base=os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com/v1"),
            model=os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229"),
            temperature=float(os.getenv("CLAUDE_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4096")),
        )

    def to_llm_config(self) -> LLMConfig:
        """Convert to LLMConfig."""
        return LLMConfig(
            provider=ProviderType.CLAUDE,
            api_key=self.api_key,
            api_base=self.api_base,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )


@dataclass
class LLMSettings:
    """
    Main LLM settings container.

    Manages configuration for all LLM providers and determines which to use.
    """
    # Active provider
    active_provider: ProviderType = ProviderType.MISTRAL

    # Provider-specific settings
    mistral: MistralSettings = field(default_factory=MistralSettings)
    claude: ClaudeSettings = field(default_factory=ClaudeSettings)

    # Feature flags
    llm_enabled: bool = True
    fallback_to_rules: bool = True  # Use rule-based NLP if LLM unavailable
    cache_responses: bool = True
    cache_ttl_seconds: int = 300

    # Rate limiting
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 100000

    # Logging
    log_prompts: bool = False  # For debugging (disable in production)
    log_responses: bool = False

    @classmethod
    def from_env(cls) -> "LLMSettings":
        """Create settings from environment variables."""
        provider_str = os.getenv("LLM_PROVIDER", "mistral").lower()
        provider_map = {
            "mistral": ProviderType.MISTRAL,
            "claude": ProviderType.CLAUDE,
            "anthropic": ProviderType.CLAUDE,
            "openai": ProviderType.OPENAI,
            "ollama": ProviderType.OLLAMA,
        }
        active_provider = provider_map.get(provider_str, ProviderType.MISTRAL)

        return cls(
            active_provider=active_provider,
            mistral=MistralSettings.from_env(),
            claude=ClaudeSettings.from_env(),
            llm_enabled=os.getenv("LLM_ENABLED", "true").lower() == "true",
            fallback_to_rules=os.getenv("LLM_FALLBACK_TO_RULES", "true").lower() == "true",
            cache_responses=os.getenv("LLM_CACHE_RESPONSES", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("LLM_CACHE_TTL_SECONDS", "300")),
            max_requests_per_minute=int(os.getenv("LLM_MAX_REQUESTS_PER_MINUTE", "60")),
            max_tokens_per_minute=int(os.getenv("LLM_MAX_TOKENS_PER_MINUTE", "100000")),
            log_prompts=os.getenv("LLM_LOG_PROMPTS", "false").lower() == "true",
            log_responses=os.getenv("LLM_LOG_RESPONSES", "false").lower() == "true",
        )

    def get_active_config(self) -> LLMConfig:
        """Get LLMConfig for the active provider."""
        if self.active_provider == ProviderType.MISTRAL:
            return self.mistral.to_llm_config()
        elif self.active_provider == ProviderType.CLAUDE:
            return self.claude.to_llm_config()
        else:
            # Default to Mistral
            return self.mistral.to_llm_config()

    def is_configured(self) -> bool:
        """Check if the active provider is properly configured."""
        if self.active_provider == ProviderType.MISTRAL:
            return bool(self.mistral.api_key)
        elif self.active_provider == ProviderType.CLAUDE:
            return bool(self.claude.api_key)
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without sensitive data)."""
        return {
            "active_provider": self.active_provider.value,
            "llm_enabled": self.llm_enabled,
            "fallback_to_rules": self.fallback_to_rules,
            "is_configured": self.is_configured(),
            "mistral": {
                "model": self.mistral.model,
                "temperature": self.mistral.temperature,
                "max_tokens": self.mistral.max_tokens,
                "api_key_set": bool(self.mistral.api_key),
            },
            "claude": {
                "model": self.claude.model,
                "temperature": self.claude.temperature,
                "max_tokens": self.claude.max_tokens,
                "api_key_set": bool(self.claude.api_key),
            },
        }


# Singleton pattern for settings
_settings: Optional[LLMSettings] = None


def get_llm_settings() -> LLMSettings:
    """
    Get LLM settings singleton.

    Returns:
        LLMSettings instance loaded from environment
    """
    global _settings
    if _settings is None:
        _settings = LLMSettings.from_env()
    return _settings


def reload_settings() -> LLMSettings:
    """
    Reload settings from environment.

    Useful when environment variables change during runtime.

    Returns:
        New LLMSettings instance
    """
    global _settings
    _settings = LLMSettings.from_env()
    return _settings


# Environment variable template for documentation
ENV_TEMPLATE = """
# ==============================================
# SYNAPSIX LLM Configuration
# ==============================================

# Active LLM Provider (mistral, claude, openai, ollama)
LLM_PROVIDER=mistral

# Enable/Disable LLM features
LLM_ENABLED=true
LLM_FALLBACK_TO_RULES=true

# Mistral Configuration
MISTRAL_API_KEY=your-mistral-api-key
MISTRAL_MODEL=mistral-large-latest
MISTRAL_TEMPERATURE=0.3
MISTRAL_MAX_TOKENS=2048
MISTRAL_SAFE_PROMPT=true

# Claude Configuration (for future use)
ANTHROPIC_API_KEY=your-anthropic-api-key
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_TEMPERATURE=0.3
CLAUDE_MAX_TOKENS=4096

# Caching
LLM_CACHE_RESPONSES=true
LLM_CACHE_TTL_SECONDS=300

# Rate Limiting
LLM_MAX_REQUESTS_PER_MINUTE=60
LLM_MAX_TOKENS_PER_MINUTE=100000

# Debugging (disable in production)
LLM_LOG_PROMPTS=false
LLM_LOG_RESPONSES=false
"""
