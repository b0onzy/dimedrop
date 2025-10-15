# DimeDrop Auth Service
# JWT validation for Auth0 integration

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional

# Talon: Dictate 'add JWT validation' here
security = HTTPBearer()

class User(BaseModel):
    user_id: str
    email: Optional[str] = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Validate Auth0 JWT token and extract user information"""
    try:
        token = credentials.credentials
        # Get Auth0 configuration from environment
        auth0_domain = os.getenv("AUTH0_DOMAIN", "")
        auth0_client_id = os.getenv("AUTH0_CLIENT_ID", "")

        # Decode JWT without verification for now (in production, verify with Auth0 public key)
        # For production, implement proper JWT verification with Auth0's JWKS
        payload = jwt.get_unverified_claims(token)

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid JWT: missing user_id"
            )

        return User(
            user_id=user_id,
            email=payload.get("email")
        )

    except HTTPException:
        # Re-raise HTTPExceptions (like the one for missing user_id)
        raise
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT validation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get user if authenticated, None if not"""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None