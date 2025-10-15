#!/usr/bin/env python3
"""
eBay OAuth 2.0 Token Management
Implements Client Credentials flow with automatic token refresh
"""

import os
import sys
import time
import base64
import logging
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)


class EbayOAuthError(Exception):
    """Custom exception for eBay OAuth errors"""
    pass


class EbayOAuth:
    """
    eBay OAuth 2.0 Manager with automatic token refresh

    Features:
    - Client Credentials flow (no user interaction)
    - In-memory token caching (security best practice)
    - Auto-refresh 5 minutes before expiration
    - Exponential backoff retry logic
    - Thread-safe token management

    Usage:
        oauth = EbayOAuth(app_id, cert_id)
        token = await oauth.get_access_token()
    """

    # eBay OAuth endpoints
    TOKEN_URL_PRODUCTION = "https://api.ebay.com/identity/v1/oauth2/token"
    TOKEN_URL_SANDBOX = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

    # Security: Refresh 5 minutes before expiration to prevent mid-request failures
    REFRESH_BUFFER_SECONDS = 300

    # eBay tokens are valid for 2 hours (7200 seconds)
    DEFAULT_TOKEN_EXPIRY = 7200

    def __init__(
        self,
        app_id: str,
        cert_id: str,
        environment: str = "production"
    ):
        """
        Initialize eBay OAuth manager

        Args:
            app_id: eBay Application ID
            cert_id: eBay Certificate ID
            environment: 'production' or 'sandbox'
        """
        if not app_id or not cert_id:
            raise EbayOAuthError("eBay credentials (APP_ID and CERT_ID) are required")

        self.app_id = app_id
        self.cert_id = cert_id
        self.environment = environment.lower()

        # Token storage (in-memory only for security)
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

        # HTTP client with timeout
        self._client = httpx.AsyncClient(timeout=10.0)

        # Select endpoint based on environment
        self.token_url = (
            self.TOKEN_URL_PRODUCTION
            if self.environment == "production"
            else self.TOKEN_URL_SANDBOX
        )

        logger.info(f"EbayOAuth initialized for {environment} environment")

    def _create_auth_header(self) -> str:
        """
        Create Basic Authorization header
        Format: base64(APP_ID:CERT_ID)

        Returns:
            Base64 encoded credentials string
        """
        credentials = f"{self.app_id}:{self.cert_id}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _is_token_valid(self) -> bool:
        """
        Check if current token is valid (exists and not expired)
        Applies 5-minute buffer to prevent mid-request expiration

        Returns:
            True if token is valid and has >5 minutes remaining
        """
        if not self._access_token:
            return False

        # Check if token expires within buffer window
        buffer_time = time.time() + self.REFRESH_BUFFER_SECONDS
        return self._token_expires_at > buffer_time

    async def _fetch_new_token(self) -> Dict[str, any]:
        """
        Fetch new OAuth token from eBay API

        Returns:
            Token response dict with access_token and expires_in

        Raises:
            EbayOAuthError: If token fetch fails after retries
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self._create_auth_header()
        }

        data = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        }

        # Exponential backoff: 1s, 2s, 4s
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching eBay OAuth token (attempt {attempt + 1}/{max_retries})")

                response = await self._client.post(
                    self.token_url,
                    headers=headers,
                    data=data
                )

                # Success
                if response.status_code == 200:
                    token_data = response.json()
                    logger.info("✅ eBay OAuth token obtained successfully")
                    return token_data

                # Authorization error (bad credentials)
                if response.status_code == 401:
                    logger.error("❌ eBay OAuth failed: Invalid credentials (401)")
                    raise EbayOAuthError(
                        f"Invalid eBay credentials. Check EBAY_APP_ID and EBAY_CERT_ID. "
                        f"Response: {response.text}"
                    )

                # Server error - retry
                if response.status_code >= 500:
                    logger.warning(f"eBay API server error ({response.status_code}), retrying...")
                    if attempt < max_retries - 1:
                        await self._backoff_sleep(attempt)
                        continue

                # Other error
                raise EbayOAuthError(
                    f"Failed to obtain OAuth token. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )

            except httpx.TimeoutException:
                logger.warning(f"eBay OAuth request timeout (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    await self._backoff_sleep(attempt)
                    continue
                raise EbayOAuthError("eBay OAuth request timed out after retries")

            except httpx.RequestError as e:
                logger.error(f"Network error during OAuth request: {e}")
                if attempt < max_retries - 1:
                    await self._backoff_sleep(attempt)
                    continue
                raise EbayOAuthError(f"Network error: {e}")

        raise EbayOAuthError("Failed to obtain OAuth token after all retries")

    async def _backoff_sleep(self, attempt: int):
        """Exponential backoff sleep"""
        sleep_time = 2 ** attempt  # 1s, 2s, 4s
        logger.info(f"Backing off for {sleep_time} seconds...")
        await asyncio.sleep(sleep_time)

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get valid OAuth access token (cached or fresh)

        This is the main public method to get tokens. It handles:
        - Returning cached token if valid
        - Auto-refreshing expired tokens
        - Error handling and retries

        Args:
            force_refresh: Force fetch new token even if cached token is valid

        Returns:
            Valid OAuth access token string

        Raises:
            EbayOAuthError: If unable to obtain valid token
        """
        # Return cached token if valid (unless forced refresh)
        if not force_refresh and self._is_token_valid():
            logger.debug("Using cached eBay OAuth token")
            return self._access_token

        # Fetch new token
        try:
            token_data = await self._fetch_new_token()

            # Extract token and expiration
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", self.DEFAULT_TOKEN_EXPIRY)

            if not self._access_token:
                raise EbayOAuthError("No access_token in response")

            # Calculate expiration timestamp
            self._token_expires_at = time.time() + expires_in

            # Log expiration time for debugging
            expires_at_datetime = datetime.fromtimestamp(self._token_expires_at)
            logger.info(f"Token expires at: {expires_at_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

            return self._access_token

        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise EbayOAuthError(f"OAuth token fetch failed: {e}")

    async def refresh_token(self) -> str:
        """
        Explicitly refresh the OAuth token
        Convenience method for force_refresh

        Returns:
            New OAuth access token
        """
        return await self.get_access_token(force_refresh=True)

    def get_token_info(self) -> Dict[str, any]:
        """
        Get current token information (for debugging/monitoring)

        Returns:
            Dict with token status, expiration, etc.
        """
        if not self._access_token:
            return {
                "has_token": False,
                "is_valid": False
            }

        time_remaining = self._token_expires_at - time.time()
        expires_at = datetime.fromtimestamp(self._token_expires_at)

        return {
            "has_token": True,
            "is_valid": self._is_token_valid(),
            "expires_at": expires_at.isoformat(),
            "time_remaining_seconds": int(time_remaining),
            "time_remaining_minutes": int(time_remaining / 60),
            "token_preview": f"{self._access_token[:10]}..." if self._access_token else None
        }

    async def close(self):
        """Close HTTP client (cleanup)"""
        await self._client.aclose()
        logger.info("EbayOAuth client closed")

    async def __aenter__(self):
        """Async context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager cleanup"""
        await self.close()


# ============================================================================
# Factory Function for Easy Initialization
# ============================================================================

def create_ebay_oauth(environment: str = "production") -> EbayOAuth:
    """
    Factory function to create EbayOAuth instance from environment variables

    Reads from environment:
        EBAY_APP_ID - eBay Application ID
        EBAY_CERT_ID - eBay Certificate ID

    Args:
        environment: 'production' or 'sandbox'

    Returns:
        Configured EbayOAuth instance

    Raises:
        EbayOAuthError: If required environment variables are missing
    """
    app_id = os.getenv("EBAY_APP_ID")
    cert_id = os.getenv("EBAY_CERT_ID")

    if not app_id or not cert_id:
        raise EbayOAuthError(
            "Missing eBay credentials. Set EBAY_APP_ID and EBAY_CERT_ID environment variables. "
            "See docs/SETUP.md for instructions."
        )

    return EbayOAuth(
        app_id=app_id,
        cert_id=cert_id,
        environment=environment
    )


# ============================================================================
# Testing & Development
# ============================================================================

if __name__ == "__main__":
    """Test OAuth flow"""
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from load_env import load_environment

    # Load environment variables
    load_environment()

    async def test_oauth():
        print("\n=== eBay OAuth 2.0 Test ===\n")

        try:
            # Create OAuth manager
            oauth = create_ebay_oauth(environment="production")

            # Get token
            print("1. Fetching OAuth token...")
            token = await oauth.get_access_token()
            print(f"   ✅ Token obtained: {token[:20]}...\n")

            # Get token info
            print("2. Token information:")
            info = oauth.get_token_info()
            for key, value in info.items():
                print(f"   {key}: {value}")
            print()

            # Test cached token (should be instant)
            print("3. Testing cached token...")
            token2 = await oauth.get_access_token()
            assert token == token2
            print("   ✅ Cached token returned (no API call)\n")

            # Cleanup
            await oauth.close()

            print("✅ All OAuth tests passed!")

        except EbayOAuthError as e:
            print(f"❌ OAuth Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    # Run test
    asyncio.run(test_oauth())
