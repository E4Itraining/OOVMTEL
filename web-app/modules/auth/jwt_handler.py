"""
JWT Authentication Handler for OOVMTEL
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import get_auth_config

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)

# API Key scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Pydantic Models
class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    roles: List[str] = []
    exp: Optional[datetime] = None


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: List[str] = []


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


class JWTHandler:
    """JWT token handler for authentication."""

    def __init__(self):
        self.config = get_auth_config()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def get_user(self, username: str) -> Optional[UserInDB]:
        """Get user from database (demo: in-memory)."""
        if username in self.config.default_users:
            user_dict = self.config.default_users[username]
            return UserInDB(**user_dict)
        return None

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with username and password."""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.config.access_token_expire_minutes
            )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=self.config.refresh_token_expire_days
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            self.config.secret_key,
            algorithm=self.config.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )
            username: str = payload.get("sub")
            roles: List[str] = payload.get("roles", [])
            if username is None:
                return None
            return TokenData(username=username, roles=roles)
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None

    def verify_api_key(self, api_key: str) -> Optional[dict]:
        """Verify an API key."""
        api_keys = self.config.get_api_keys()
        if api_key in api_keys:
            return api_keys[api_key]
        return None


# Global JWT handler instance
_jwt_handler: Optional[JWTHandler] = None


def get_jwt_handler() -> JWTHandler:
    """Get or create JWT handler instance."""
    global _jwt_handler
    if _jwt_handler is None:
        _jwt_handler = JWTHandler()
    return _jwt_handler


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[User]:
    """
    Get current user from JWT token or API key.
    Returns None if auth is disabled or no credentials provided.
    """
    config = get_auth_config()
    jwt_handler = get_jwt_handler()

    # If auth is disabled, return a default admin user
    if not config.auth_enabled:
        return User(
            username="anonymous",
            email="anonymous@oovmtel.local",
            full_name="Anonymous User",
            disabled=False,
            roles=["admin", "operator", "viewer"]
        )

    # Try API key first
    if api_key:
        key_data = jwt_handler.verify_api_key(api_key)
        if key_data:
            return User(
                username=f"api_key:{key_data['name']}",
                full_name=key_data["name"],
                disabled=False,
                roles=key_data["roles"]
            )

    # Try JWT token
    if token:
        token_data = jwt_handler.verify_token(token)
        if token_data:
            user = jwt_handler.get_user(token_data.username)
            if user:
                return User(
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    disabled=user.disabled,
                    roles=user.roles
                )

    # No valid credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active (non-disabled) user."""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_roles(required_roles: List[str]):
    """Dependency factory for role-based access control."""
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        for role in required_roles:
            if role in current_user.roles:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {required_roles}"
        )
    return role_checker
