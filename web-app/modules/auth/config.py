"""
Authentication Configuration
"""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class AuthConfig:
    """Authentication configuration settings."""

    # JWT Settings
    secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "oovmtel-super-secret-key-change-in-production-2024"
    )
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    refresh_token_expire_days: int = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    # Authentication Settings
    auth_enabled: bool = os.getenv("AUTH_ENABLED", "true").lower() == "true"

    # Default users (for demo - in production use database)
    default_users: dict = None

    def __post_init__(self):
        if self.default_users is None:
            self.default_users = {
                "admin": {
                    "username": "admin",
                    "full_name": "Administrator",
                    "email": "admin@oovmtel.local",
                    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                    "disabled": False,
                    "roles": ["admin", "operator", "viewer"],
                },
                "operator": {
                    "username": "operator",
                    "full_name": "Plant Operator",
                    "email": "operator@oovmtel.local",
                    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                    "disabled": False,
                    "roles": ["operator", "viewer"],
                },
                "viewer": {
                    "username": "viewer",
                    "full_name": "Dashboard Viewer",
                    "email": "viewer@oovmtel.local",
                    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
                    "disabled": False,
                    "roles": ["viewer"],
                },
            }

    # API Key Settings (alternative auth method)
    api_key_header: str = "X-API-Key"
    api_keys: dict = None

    def get_api_keys(self) -> dict:
        """Get configured API keys."""
        if self.api_keys is None:
            # Load from environment or use defaults for demo
            self.api_keys = {
                os.getenv("API_KEY_ADMIN", "oovmtel-admin-key-2024"): {
                    "name": "Admin API Key",
                    "roles": ["admin", "operator", "viewer"],
                },
                os.getenv("API_KEY_OPERATOR", "oovmtel-operator-key-2024"): {
                    "name": "Operator API Key",
                    "roles": ["operator", "viewer"],
                },
                os.getenv("API_KEY_VIEWER", "oovmtel-viewer-key-2024"): {
                    "name": "Viewer API Key",
                    "roles": ["viewer"],
                },
            }
        return self.api_keys


@lru_cache()
def get_auth_config() -> AuthConfig:
    """Get cached authentication configuration."""
    return AuthConfig()
