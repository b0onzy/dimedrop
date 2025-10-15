"""
API Manager for DimeDrop
Handles API calls to FastAPI backend with caching.
"""

import os
import requests
from functools import lru_cache
from typing import Dict, List, Optional
import cv2
import numpy as np

# Configuration
API_BASE_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")


class APIManager:
    """Handles API calls to FastAPI backend with caching."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    @lru_cache(maxsize=100)
    def _cached_get(self, url: str) -> Dict:
        """Cached GET request."""
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            # Return mock data for demo
            return self._get_mock_data(url)

    def _get_mock_data(self, url: str) -> Dict:
        """Return mock data when API is unavailable."""
        if 'prices' in url:
            return {
                "avg_price": 152.50,
                "high": 160.0,
                "low": 145.5,
                "volume": 25,
                "trend": "up"
            }
        elif 'sentiment' in url:
            return {
                "flip_score": 85,
                "sentiment_breakdown": {"positive": 15, "negative": 3, "neutral": 7}
            }
        elif 'portfolio' in url:
            return {"portfolio": []}
        return {}

    def get_prices(self, card_name: str) -> Dict:
        """Get price data for a card."""
        url = f"{self.base_url}/prices?card={card_name}"
        return self._cached_get(url)

    def get_sentiment(self, card_name: str) -> Dict:
        """Get sentiment analysis for a card."""
        url = f"{self.base_url}/sentiment/{card_name}"
        return self._cached_get(url)

    def scan_card(self, image_data: bytes, token: Optional[str] = None) -> Dict:
        """Scan card using vision API."""
        url = f"{self.base_url}/vision/scan"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            # Preprocess image with OpenCV
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                # Resize for efficiency
                img = cv2.resize(img, (640, 480))
                # Convert back to bytes
                _, encoded_img = cv2.imencode('.jpg', img)
                img_bytes = encoded_img.tobytes()
            else:
                img_bytes = image_data

            files = {'file': ('card.jpg', img_bytes, 'image/jpeg')}
            response = self.session.post(url, files=files, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {
                "card_name": "Unknown Card",
                "confidence": 0.0,
                "error": "Vision API unavailable - using mock data"
            }

    def get_portfolio(self, token: str) -> List[Dict]:
        """Get user portfolio."""
        url = f"{self.base_url}/portfolio"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = self.session.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            result = response.json()
            return result.get("portfolio", [])
        except requests.RequestException:
            return []

    def update_portfolio(self, action: str, card_data: Dict, token: str) -> Dict:
        """Update portfolio (add/update/delete)."""
        url = f"{self.base_url}/portfolio"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        if action == "delete":
            # DELETE request
            response = self.session.delete(f"{url}/{card_data['id']}", headers=headers)
        else:
            # POST request for add/update
            response = self.session.post(url, json=card_data, headers=headers)

        try:
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"error": "Portfolio update failed"}
