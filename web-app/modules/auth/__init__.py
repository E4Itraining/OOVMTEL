"""
Authentication Module for OOVMTEL Unified View
JWT-based authentication with OAuth2
"""

from .jwt_handler import (
    JWTHandler,
    Token,
    TokenData,
    User,
    UserInDB,
    get_current_user,
    get_current_active_user,
    oauth2_scheme,
)
from .config import AuthConfig, get_auth_config

__all__ = [
    "JWTHandler",
    "Token",
    "TokenData",
    "User",
    "UserInDB",
    "get_current_user",
    "get_current_active_user",
    "oauth2_scheme",
    "AuthConfig",
    "get_auth_config",
]
