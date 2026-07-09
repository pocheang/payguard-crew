"""
Enterprise JWT authentication and authorization.
Supports role-based access control (RBAC) and token refresh.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import get_settings


# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY is required. Generate with:\n"
        "python -c \"import secrets; print(secrets.token_urlsafe(64))\""
    )

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    username: str
    roles: list[str]
    exp: datetime
    iat: datetime
    token_type: str  # "access" or "refresh"


class User(BaseModel):
    """User model."""
    user_id: str
    username: str
    email: str
    roles: list[str]
    is_active: bool = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id": user.user_id,
        "username": user.username,
        "roles": user.roles,
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "access"
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user: User) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "user_id": user.user_id,
        "username": user.username,
        "roles": user.roles,
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "refresh"
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        token_data = TokenData(
            user_id=payload["user_id"],
            username=payload["username"],
            roles=payload["roles"],
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
            token_type=payload.get("token_type", "access")
        )
        return token_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Dependency to get current authenticated user.

    Usage:
        @app.get("/protected")
        def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    token = credentials.credentials
    token_data = decode_token(token)

    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return token_data


class RoleChecker:
    """Dependency to check user roles."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: TokenData = Depends(get_current_user)) -> TokenData:
        """Check if user has required role."""
        if not any(role in self.allowed_roles for role in user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {self.allowed_roles}",
            )
        return user


# Predefined role checkers
require_admin = RoleChecker(["admin", "super_admin"])
require_compliance = RoleChecker(["admin", "super_admin", "compliance_officer"])
require_analyst = RoleChecker(["admin", "super_admin", "compliance_officer", "aml_analyst", "kyc_reviewer"])


def validate_jwt_config():
    """Validate JWT configuration on startup."""
    settings = get_settings()

    # Validate in ALL environments
    if not JWT_SECRET_KEY:
        raise ValueError(
            "JWT_SECRET_KEY is required in all environments"
        )

    if len(JWT_SECRET_KEY) < 32:
        raise ValueError(
            "JWT_SECRET_KEY must be at least 32 characters long for security"
        )

    # Additional checks for production
    if settings.app_env in ["prod", "production"]:
        if len(JWT_SECRET_KEY) < 64:
            raise ValueError(
                "Production JWT_SECRET_KEY should be at least 64 characters"
            )
