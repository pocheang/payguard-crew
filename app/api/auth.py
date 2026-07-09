"""
Authentication API routes for JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr

from app.core.auth import (
    User,
    TokenData,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    get_password_hash,
    get_current_user,
)

router = APIRouter(tags=["authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserCreateRequest(BaseModel):
    """User creation request"""
    username: str
    email: EmailStr
    password: str
    roles: list[str] = ["viewer"]


# Mock user database (replace with real database in production)
# Lazy initialization to avoid bcrypt initialization issues
_MOCK_USERS_CACHE = None

def get_mock_users():
    global _MOCK_USERS_CACHE
    if _MOCK_USERS_CACHE is None:
        _MOCK_USERS_CACHE = {
            "admin": {
                "user_id": "user_001",
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": get_password_hash("admin123"),
                "roles": ["super_admin"],
                "is_active": True,
            },
            "demo": {
                "user_id": "user_002",
                "username": "demo",
                "email": "demo@example.com",
                "password_hash": get_password_hash("demo123"),
                "roles": ["analyst"],
                "is_active": True,
            }
        }
    return _MOCK_USERS_CACHE


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - returns JWT tokens.

    Default users:
    - admin / admin123 (super_admin role)
    - demo / demo123 (analyst role)
    """
    # Check if user exists
    user_data = get_mock_users().get(request.username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Verify password
    if not verify_password(request.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Check if user is active
    if not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Create user object
    user = User(
        user_id=user_data["user_id"],
        username=user_data["username"],
        email=user_data["email"],
        roles=user_data["roles"],
        is_active=user_data["is_active"],
    )

    # Generate tokens
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        # Decode refresh token
        token_data = decode_token(request.refresh_token)

        # Verify it's a refresh token
        if token_data.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Get user data (in production, fetch from database)
        user_data = get_mock_users().get(token_data.username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Create user object
        user = User(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            roles=user_data["roles"],
            is_active=user_data["is_active"],
        )

        # Generate new tokens
        new_access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

        return LoginResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=1800,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
async def logout(user: TokenData = Depends(get_current_user)):
    """
    Logout endpoint (client should discard tokens).

    In production, implement token blacklist/revocation.
    """
    return {
        "message": "Successfully logged out",
        "user_id": user.user_id,
    }


@router.get("/me")
async def get_current_user_info(user: TokenData = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return {
        "user_id": user.user_id,
        "username": user.username,
        "roles": user.roles,
        "token_expires_at": user.exp.isoformat(),
    }
