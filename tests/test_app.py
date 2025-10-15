"""
DimeDrop Tests
Basic test suite for the Gradio application components.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from components import (
    APIManager,
    AuthManager,
    ScanCardComponent,
    PriceTrackerComponent,
    SentimentAnalyzerComponent,
    PortfolioManagerComponent
)


class TestAPIManager:
    """Test API manager functionality."""

    def test_init(self):
        """Test API manager initialization."""
        api = APIManager()
        assert api.base_url == "http://localhost:8000"
        assert api.session is not None

    def test_get_mock_data(self):
        """Test mock data generation."""
        api = APIManager()
        prices_data = api._get_mock_data("http://localhost:8000/prices?card=test")
        assert "avg_price" in prices_data
        assert isinstance(prices_data["avg_price"], float)

        sentiment_data = api._get_mock_data("http://localhost:8000/sentiment/test")
        assert "flip_score" in sentiment_data
        assert isinstance(sentiment_data["flip_score"], int)


class TestAuthManager:
    """Test authentication manager."""

    def test_init(self):
        """Test auth manager initialization."""
        auth = AuthManager()
        # Just check that the attributes exist
        assert hasattr(auth, 'domain')
        assert hasattr(auth, 'client_id')
        assert hasattr(auth, 'audience')

    def test_get_login_url(self):
        """Test login URL generation."""
        auth = AuthManager()
        url = auth.get_login_url()
        assert url == "#"  # Returns # when config is missing


class TestDimeDropApp:
    """Test main app functionality."""

    @patch('app.gr')
    def test_init(self, mock_gr):
        """Test app initialization."""
        from app import DimeDropApp
        app = DimeDropApp()
        assert app.current_user is None
        assert app.current_token is None
        assert isinstance(app.auth, AuthManager)
        assert isinstance(app.api, APIManager)


# Integration test placeholder
@patch('app.gr')
def test_app_creation(mock_gr):
    """Test that app can be created without errors."""
    from app import DimeDropApp
    app = DimeDropApp()
    interface = app.create_interface()
    assert interface is not None


class TestComponents:
    """Test individual components."""

    def test_scan_card_no_auth(self):
        """Test scan card without authentication."""
        api = APIManager()
        auth = AuthManager()
        scan_component = ScanCardComponent(api, auth)
        result = scan_component.scan_card(None, None)
        assert isinstance(result, str)
        assert "Please login" in result.lower()

    def test_scan_card_no_image(self):
        """Test scan card without image."""
        api = APIManager()
        auth = AuthManager()
        scan_component = ScanCardComponent(api, auth)
        result = scan_component.scan_card(None, "fake_token")
        assert isinstance(result, str)
        assert "upload a card image" in result.lower()

    def test_get_price_empty(self):
        """Test price tracking with empty input."""
        api = APIManager()
        auth = AuthManager()
        price_component = PriceTrackerComponent(api, auth)
        result = price_component.get_price_data("", "fake_token")
        assert "error" in result
        assert "enter a card name" in result["error"].lower()

    def test_sentiment_empty(self):
        """Test sentiment analysis with empty input."""
        api = APIManager()
        auth = AuthManager()
        sentiment_component = SentimentAnalyzerComponent(api, auth)
        result = sentiment_component.analyze_sentiment("", "fake_token")
        assert "error" in result
        assert "enter text" in result["error"].lower()

    def test_sentiment_analysis(self):
        """Test sentiment analysis with sample text."""
        api = APIManager()
        auth = AuthManager()
        sentiment_component = SentimentAnalyzerComponent(api, auth)
        result = sentiment_component.analyze_sentiment("This stock is bullish and will rise significantly", "fake_token")
        assert "flip_score" in result
        assert isinstance(result["flip_score"], int)
        assert result["flip_score"] > 50  # Should be positive
        assert "sentiment_breakdown" in result

    def test_portfolio_no_auth(self):
        """Test portfolio access without authentication."""
        api = APIManager()
        auth = AuthManager()
        portfolio_component = PortfolioManagerComponent(api, auth)
        result = portfolio_component.update_portfolio("Add", "Test Card", 1, None)
        assert "Please login" in result


if __name__ == "__main__":
    pytest.main([__file__])
