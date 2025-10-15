"""
Authentication Manager for DimeDrop
Handles Auth0 authentication and JWT validation.
"""

import os
import time
from typing import Dict, Optional
from jose import jwt, JWTError

# Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")


class AuthManager:
    """Handles Auth0 authentication and JWT validation."""

    def __init__(self):
        self.domain = AUTH0_DOMAIN
        self.client_id = AUTH0_CLIENT_ID
        self.audience = AUTH0_AUDIENCE

    def get_login_url(self) -> str:
        """Generate Auth0 login URL."""
        if not all([self.domain, self.client_id, self.audience]):
            return "#"
        return f"https://{self.domain}/authorize?response_type=code&client_id={self.client_id}&redirect_uri=http://localhost:7860/callback&scope=openid profile email&audience={self.audience}"

    def validate_jwt(self, token: str) -> Optional[Dict]:
        """Validate JWT token and return payload."""
        try:
            # In production, fetch JWKS from Auth0
            # For demo, we'll mock validation
            payload = jwt.get_unverified_claims(token)
            if payload.get('exp', 0) > time.time():
                return payload
        except JWTError:
            pass
        return None
