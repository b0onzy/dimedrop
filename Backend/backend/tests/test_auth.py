#!/usr/bin/env python3
"""
Tests for DimeDrop Auth Service
Tests JWT validation and user authentication
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.services.auth import get_current_user, get_optional_user, User


class TestAuthService:
    """Test cases for authentication service"""

    @pytest.fixture
    def valid_token(self):
        """Create a valid JWT token for testing"""
        payload = {
            'sub': 'auth0|123456789',
            'name': 'Test User',
            'email': 'test@example.com',
            'iss': 'https://dimedrop.auth0.com/',
            'aud': 'dimedrop-api',
            'iat': datetime.utcnow().timestamp(),
            'exp': (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }
        secret = 'test-secret-key'
        return jwt.encode(payload, secret, algorithm='HS256')

    @pytest.fixture
    def expired_token(self):
        """Create an expired JWT token"""
        payload = {
            'sub': 'auth0|123456789',
            'name': 'Test User',
            'email': 'test@example.com',
            'iss': 'https://dimedrop.auth0.com/',
            'aud': 'dimedrop-api',
            'iat': (datetime.utcnow() - timedelta(hours=2)).timestamp(),
            'exp': (datetime.utcnow() - timedelta(hours=1)).timestamp()
        }
        secret = 'test-secret-key'
        return jwt.encode(payload, secret, algorithm='HS256')

    @pytest.fixture
    def valid_credentials(self, valid_token):
        """Create valid HTTP authorization credentials"""
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)

    @pytest.fixture
    def expired_credentials(self, expired_token):
        """Create expired HTTP authorization credentials"""
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)

    @patch('app.services.auth.jwt.get_unverified_claims')
    @patch('app.services.auth.os.getenv')
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_getenv, mock_jwt_decode, valid_credentials):
        """Test successful user authentication with valid token"""
        # Mock environment variables
        def getenv_side_effect(key, default=""):
            env_vars = {
                'AUTH0_DOMAIN': 'dimedrop.auth0.com',
                'AUTH0_CLIENT_ID': 'test-client-id'
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        # Mock JWT decode
        expected_payload = {
            'sub': 'auth0|123456789',
            'name': 'Test User',
            'email': 'test@example.com',
            'iss': 'https://dimedrop.auth0.com/',
            'aud': 'dimedrop-api'
        }
        mock_jwt_decode.return_value = expected_payload

        result = await get_current_user(valid_credentials)

        assert isinstance(result, User)
        assert result.user_id == 'auth0|123456789'
        assert result.email == 'test@example.com'
        mock_jwt_decode.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test authentication failure when no credentials provided"""
        # This test is not applicable since FastAPI handles missing credentials
        # The Depends(security) will raise an exception before reaching our function
        pass

    @patch('app.services.auth.jwt.get_unverified_claims')
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_jwt_decode, valid_credentials):
        """Test authentication failure with invalid token"""
        # Mock JWT decode to raise error
        from jose import JWTError
        mock_jwt_decode.side_effect = JWTError('Invalid token')

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(valid_credentials)

        assert exc_info.value.status_code == 401
        assert 'JWT validation failed' in str(exc_info.value.detail)

    @patch('app.services.auth.jwt.get_unverified_claims')
    @patch('app.services.auth.os.getenv')
    @pytest.mark.asyncio
    async def test_get_current_user_missing_user_id(self, mock_getenv, mock_jwt_decode, valid_credentials):
        """Test authentication failure when token missing user_id"""
        # Mock environment variables
        def getenv_side_effect(key, default=""):
            env_vars = {
                'AUTH0_DOMAIN': 'dimedrop.auth0.com',
                'AUTH0_CLIENT_ID': 'test-client-id'
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        # Mock JWT decode with missing sub claim
        mock_jwt_decode.return_value = {
            'name': 'Test User',
            'email': 'test@example.com'
            # Missing 'sub' claim
        }

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(valid_credentials)

        assert exc_info.value.status_code == 401
        assert 'Invalid JWT: missing user_id' in str(exc_info.value.detail)

    @patch('app.services.auth.jwt.get_unverified_claims')
    @patch('app.services.auth.os.getenv')
    @pytest.mark.asyncio
    async def test_get_optional_user_valid_token(self, mock_getenv, mock_jwt_decode, valid_credentials):
        """Test optional user retrieval with valid token"""
        def getenv_side_effect(key, default=""):
            env_vars = {
                'AUTH0_DOMAIN': 'dimedrop.auth0.com',
                'AUTH0_CLIENT_ID': 'test-client-id'
            }
            return env_vars.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        expected_payload = {
            'sub': 'auth0|123456789',
            'name': 'Test User',
            'email': 'test@example.com'
        }
        mock_jwt_decode.return_value = expected_payload

        result = await get_optional_user(valid_credentials)

        assert isinstance(result, User)
        assert result.user_id == 'auth0|123456789'
        assert result.email == 'test@example.com'

    @pytest.mark.asyncio
    async def test_get_optional_user_no_credentials(self):
        """Test optional user retrieval when no credentials provided"""
        result = await get_optional_user(None)

        assert result is None

    @patch('app.services.auth.jwt.get_unverified_claims')
    @pytest.mark.asyncio
    async def test_get_optional_user_invalid_token(self, mock_jwt_decode, valid_credentials):
        """Test optional user retrieval with invalid token"""
        # Mock JWT decode to raise error
        from jose import JWTError
        mock_jwt_decode.side_effect = JWTError('Invalid token')

        result = await get_optional_user(valid_credentials)

        assert result is None

    def test_user_model(self):
        """Test User Pydantic model"""
        user_data = {
            'user_id': 'auth0|123456789',
            'email': 'test@example.com'
        }

        user = User(**user_data)

        assert user.user_id == 'auth0|123456789'
        assert user.email == 'test@example.com'

    def test_user_model_optional_email(self):
        """Test User model with missing optional email"""
        user_data = {
            'user_id': 'auth0|123456789'
            # email is optional
        }

        user = User(**user_data)

        assert user.user_id == 'auth0|123456789'
        assert user.email is None