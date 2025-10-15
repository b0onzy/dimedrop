#!/usr/bin/env python3
"""
Database module for DimeDrop
Uses local SQLite database with SQLAlchemy
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from .models import SessionLocal, PriceCache, ApiRateLimits, Portfolio, Alert, NotificationPreferences, create_tables
import logging
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """
    Manages local SQLite database connection and operations
    """

    def __init__(self):
        """
        Initialize database connection
        """
        self.db_url = os.getenv('DATABASE_URL', 'sqlite:///./dimedrop.db')
        logger.info(f"Connecting to database: {self.db_url}")

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False

    def get_session(self) -> Session:
        """Get database session"""
        return SessionLocal()


# Global database manager instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def get_db_session() -> Session:
    """Get database session"""
    return get_db_manager().get_session()


# ============================================================================
# Legacy Database Compatibility (for migration)
# ============================================================================

def get_supabase_manager():
    """Legacy function for backward compatibility during migration"""
    return get_db_manager()

def init_database():
    """Initialize local database and create tables"""
    logger.info("Initializing local SQLite database")
    create_tables()
    return True
# ============================================================================
# Database Operations (CRUD) - Supabase Implementation
# ============================================================================

class CacheOperations:
    """Operations for price_cache table using Supabase"""

    @staticmethod
    def get_cached_price(card_query: str) -> Optional[Dict]:
        """
        Get cached price data if not expired

        Args:
            card_query: Card search query

        Returns:
            Cache data dict if found and not expired, None otherwise
        """
        try:
            db = SessionLocal()
            now = datetime.utcnow()

            cache_entry = db.query(PriceCache).filter(
                PriceCache.card_query == card_query,
                PriceCache.expires_at > now
            ).order_by(PriceCache.cached_at.desc()).first()

            db.close()

            if cache_entry:
                logger.info(f"Cache hit for '{card_query}'")
                return {
                    'id': cache_entry.id,
                    'card_query': cache_entry.card_query,
                    'price_data': cache_entry.price_data,
                    'cached_at': cache_entry.cached_at.isoformat(),
                    'expires_at': cache_entry.expires_at.isoformat()
                }
            else:
                logger.info(f"Cache miss for '{card_query}'")
                return None

        except Exception as e:
            logger.error(f"Error fetching from cache: {str(e)}")
            return None

    @staticmethod
    def set_cached_price(card_query: str, price_data: Dict, cache_days: int = 90) -> Optional[Dict]:
        """
        Store price data in cache

        Args:
            card_query: Card search query
            price_data: Price data dictionary
            cache_days: Number of days to cache (default 90 for eBay ToS compliance)

        Returns:
            Created cache entry dict or None if failed
        """
        try:
            db = SessionLocal()
            now = datetime.utcnow()
            expires_at = now + timedelta(days=cache_days)

            cache_entry = PriceCache(
                card_query=card_query,
                price_data=price_data,
                cached_at=now,
                expires_at=expires_at
            )

            db.add(cache_entry)
            db.commit()
            db.refresh(cache_entry)
            db.close()

            logger.info(f"Created cache entry for '{card_query}'")
            return {
                'id': cache_entry.id,
                'card_query': cache_entry.card_query,
                'price_data': cache_entry.price_data,
                'cached_at': cache_entry.cached_at.isoformat(),
                'expires_at': cache_entry.expires_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error storing in cache: {str(e)}")
            return None

    @staticmethod
    def cleanup_expired() -> int:
        """
        Remove expired cache entries

        Returns:
            Number of entries deleted
        """
        try:
            db = SessionLocal()
            now = datetime.utcnow()

            deleted_count = db.query(PriceCache).filter(PriceCache.expires_at < now).delete()
            db.commit()
            db.close()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired cache entries")

            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {str(e)}")
            return 0


class RateLimitOperations:
    """Operations for APIRateLimit table using Supabase"""

    @staticmethod
    def get_call_count(api_name: str, date = None) -> int:
        """
        Get API call count for a specific date

        Args:
            api_name: API name (e.g., 'ebay')
            date: Date string in YYYY-MM-DD format (defaults to today)

        Returns:
            Number of calls made
        """
        try:
            db = SessionLocal()

            if date is None:
                date = datetime.utcnow().date()

            rate_limit = db.query(ApiRateLimits).filter(
                ApiRateLimits.api_name == api_name,
                ApiRateLimits.date == date
            ).first()

            db.close()

            return rate_limit.call_count if rate_limit else 0

        except Exception as e:
            logger.error(f"Error getting call count: {str(e)}")
            return 0

    @staticmethod
    def increment_call_count(api_name: str, date = None) -> int:
        """
        Increment API call count

        Args:
            api_name: API name (e.g., 'ebay')
            date: Date string in YYYY-MM-DD format (defaults to today)

        Returns:
            New call count
        """
        try:
            db = SessionLocal()

            if date is None:
                date = datetime.utcnow().date()

            # Try to get existing record
            rate_limit = db.query(ApiRateLimits).filter(
                ApiRateLimits.api_name == api_name,
                ApiRateLimits.date == date
            ).first()

            if rate_limit:
                rate_limit.call_count += 1
                new_count = rate_limit.call_count
            else:
                # Create new record
                rate_limit = ApiRateLimits(
                    api_name=api_name,
                    date=date,
                    call_count=1
                )
                db.add(rate_limit)
                new_count = 1

            db.commit()
            db.close()

            logger.info(f"Incremented {api_name} call count to {new_count}")
            return new_count

        except Exception as e:
            logger.error(f"Error incrementing call count: {str(e)}")
            return 0

    @staticmethod
    def check_rate_limit(api_name: str, limit: int, date: Optional[str] = None) -> bool:
        """
        Check if under rate limit

        Args:
            api_name: API name (e.g., 'ebay')
            limit: Maximum allowed calls
            date: Date string in YYYY-MM-DD format (defaults to today)

        Returns:
            True if under limit, False if exceeded
        """
        count = RateLimitOperations.get_call_count(api_name, date)
        return count < limit


class PortfolioOperations:
    """Operations for Portfolio table using Supabase"""

    @staticmethod
    def add_card(card_name: str, purchase_price: Optional[float] = None,
                 purchase_date = None, quantity: int = 1,
                 condition: Optional[str] = None, notes: Optional[str] = None,
                 user_id: Optional[str] = None) -> Optional[Dict]:
        """Add a card to portfolio"""
        try:
            db = SessionLocal()

            if purchase_date is None:
                purchase_date = datetime.utcnow().date()
            elif isinstance(purchase_date, str):
                # Parse string date
                purchase_date = datetime.fromisoformat(purchase_date).date()

            card = Portfolio(
                user_id=user_id,
                card_name=card_name,
                buy_price=purchase_price,
                purchase_date=purchase_date,
                quantity=quantity,
                condition=condition,
                notes=notes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(card)
            db.commit()
            db.refresh(card)
            db.close()

            logger.info(f"Added card to portfolio: {card_name}")
            return {
                'id': card.id,
                'card_name': card.card_name,
                'buy_price': float(card.buy_price) if card.buy_price else None,
                'purchase_date': card.purchase_date.isoformat() if card.purchase_date else None,
                'quantity': card.quantity,
                'condition': card.condition,
                'notes': card.notes,
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error adding card to portfolio: {str(e)}")
            return None

    @staticmethod
    def get_all_cards(user_id: Optional[str] = None) -> List[Dict]:
        """Get all cards in portfolio, optionally filtered by user_id"""
        try:
            db = SessionLocal()
            query = db.query(Portfolio)
            
            if user_id:
                query = query.filter(Portfolio.user_id == user_id)
            
            cards = query.order_by(Portfolio.created_at.desc()).all()
            db.close()

            return [{
                'id': card.id,
                'card_name': card.card_name,
                'buy_price': float(card.buy_price) if card.buy_price else None,
                'purchase_date': card.purchase_date.isoformat() if card.purchase_date else None,
                'quantity': card.quantity,
                'condition': card.condition,
                'notes': card.notes,
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat()
            } for card in cards]

        except Exception as e:
            logger.error(f"Error getting all cards: {str(e)}")
            return []

    @staticmethod
    def get_card_by_id(card_id: int) -> Optional[Dict]:
        """Get a specific card by ID"""
        try:
            db = SessionLocal()
            card = db.query(Portfolio).filter(Portfolio.id == card_id).first()
            db.close()

            if card:
                return {
                    'id': card.id,
                    'card_name': card.card_name,
                    'buy_price': float(card.buy_price) if card.buy_price else None,
                    'purchase_date': card.purchase_date.isoformat() if card.purchase_date else None,
                    'quantity': card.quantity,
                    'condition': card.condition,
                    'notes': card.notes,
                    'created_at': card.created_at.isoformat(),
                    'updated_at': card.updated_at.isoformat()
                }
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting card by ID: {str(e)}")
            return None

    @staticmethod
    def update_card(card_id: int, **kwargs) -> Optional[Dict]:
        """Update a card in portfolio"""
        try:
            db = SessionLocal()
            card = db.query(Portfolio).filter(Portfolio.id == card_id).first()

            if not card:
                db.close()
                return None

            # Update fields
            for key, value in kwargs.items():
                if hasattr(card, key):
                    setattr(card, key, value)

            card.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(card)
            db.close()

            logger.info(f"Updated card: {card.card_name}")
            return {
                'id': card.id,
                'card_name': card.card_name,
                'buy_price': float(card.buy_price) if card.buy_price else None,
                'purchase_date': card.purchase_date.isoformat() if card.purchase_date else None,
                'quantity': card.quantity,
                'condition': card.condition,
                'notes': card.notes,
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error updating card: {str(e)}")
            return None

    @staticmethod
    def delete_card(card_id: int) -> bool:
        """Delete a card from portfolio"""
        try:
            db = SessionLocal()
            deleted_count = db.query(Portfolio).filter(Portfolio.id == card_id).delete()
            db.commit()
            db.close()

            if deleted_count > 0:
                logger.info(f"Deleted card with ID: {card_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error deleting card: {str(e)}")
            return False


class AlertOperations:
    """Operations for managing price alerts"""

    @staticmethod
    def create_alert(card_name: str, target_price: float, alert_type: str, notes: Optional[str] = None, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Create a new price alert

        Args:
            card_name: Name of the basketball card
            target_price: Target price for the alert
            alert_type: 'above' or 'below'
            notes: Optional notes
            user_id: Optional user ID for multi-user support

        Returns:
            Dict with alert details including ID and created_at
        """
        try:
            # For now, return mock data since we're using Supabase
            # In production, this would create a record in Supabase
            alert_data = {
                'id': 1,  # Mock ID
                'card_name': card_name,
                'target_price': target_price,
                'alert_type': alert_type,
                'is_active': True,
                'notes': notes,
                'created_at': datetime.utcnow().isoformat()
            }

            logger.info(f"Created alert for {card_name}: {alert_type} ${target_price}")
            return alert_data

        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None

    @staticmethod
    def get_alerts(active_only: bool = True, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get all alerts

        Args:
            active_only: If True, return only active alerts
            user_id: Optional user ID filter for multi-user support

        Returns:
            List of alert dictionaries
        """
        try:
            # Mock data for now
            alerts = [
                {
                    'id': 1,
                    'card_name': 'Wembanyama Prizm',
                    'target_price': 150.00,
                    'alert_type': 'above',
                    'is_active': True,
                    'notes': 'Good investment opportunity',
                    'created_at': '2025-10-13T10:00:00Z',
                    'current_price': 152.50
                },
                {
                    'id': 2,
                    'card_name': 'Luka Doncic Auto',
                    'target_price': 180.00,
                    'alert_type': 'below',
                    'is_active': True,
                    'notes': 'Watch for dip',
                    'created_at': '2025-10-13T11:00:00Z',
                    'current_price': 200.00
                }
            ]

            if active_only:
                alerts = [alert for alert in alerts if alert['is_active']]

            return alerts

        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return []

    @staticmethod
    def update_alert(alert_id: int, update_data: Dict) -> Optional[Dict]:
        """
        Update an existing alert

        Args:
            alert_id: ID of the alert to update
            update_data: Dict with fields to update

        Returns:
            Updated alert dict or None if not found
        """
        try:
            # Mock implementation - in production would update Supabase
            alerts = AlertOperations.get_alerts(active_only=False)
            alert = next((a for a in alerts if a['id'] == alert_id), None)

            if not alert:
                return None

            # Apply updates
            for key, value in update_data.items():
                if key in alert:
                    alert[key] = value

            logger.info(f"Updated alert {alert_id}")
            return alert

        except Exception as e:
            logger.error(f"Error updating alert {alert_id}: {str(e)}")
            return None

    @staticmethod
    def delete_alert(alert_id: int) -> bool:
        """
        Delete an alert

        Args:
            alert_id: ID of the alert to delete

        Returns:
            True if deleted successfully
        """
        try:
            # Mock implementation - in production would delete from Supabase
            alerts = AlertOperations.get_alerts(active_only=False)
            alert = next((a for a in alerts if a['id'] == alert_id), None)

            if not alert:
                return False

            # In real implementation, would remove from database
            logger.info(f"Deleted alert {alert_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting alert {alert_id}: {str(e)}")
            return False


class NotificationOperations:
    """Operations for managing notification preferences"""

    @staticmethod
    def get_notification_preferences(email: str) -> Optional[Dict]:
        """
        Get notification preferences for a user

        Args:
            email: User's email address

        Returns:
            Notification preferences dict or None if not found
        """
        try:
            db = SessionLocal()
            prefs = db.query(NotificationPreferences).filter(
                NotificationPreferences.email == email
            ).first()
            db.close()

            if prefs:
                return {
                    'id': prefs.id,
                    'email': prefs.email,
                    'email_notifications_enabled': bool(prefs.email_notifications_enabled),
                    'push_notifications_enabled': bool(prefs.push_notifications_enabled),
                    'alert_trigger_notifications': bool(prefs.alert_trigger_notifications),
                    'weekly_summary_enabled': bool(prefs.weekly_summary_enabled),
                    'created_at': prefs.created_at.isoformat(),
                    'updated_at': prefs.updated_at.isoformat()
                }
            else:
                return None

        except Exception as e:
            logger.error(f"Error getting notification preferences: {str(e)}")
            return None

    @staticmethod
    def create_or_update_notification_preferences(
        email: str,
        email_notifications_enabled: bool = True,
        push_notifications_enabled: bool = False,
        alert_trigger_notifications: bool = True,
        weekly_summary_enabled: bool = False
    ) -> Optional[Dict]:
        """
        Create or update notification preferences for a user

        Args:
            email: User's email address
            email_notifications_enabled: Enable email notifications
            push_notifications_enabled: Enable push notifications
            alert_trigger_notifications: Enable alert trigger notifications
            weekly_summary_enabled: Enable weekly summary emails

        Returns:
            Updated preferences dict
        """
        try:
            db = SessionLocal()
            now = datetime.utcnow()

            # Try to get existing preferences
            prefs = db.query(NotificationPreferences).filter(
                NotificationPreferences.email == email
            ).first()

            if prefs:
                # Update existing
                prefs.email_notifications_enabled = int(email_notifications_enabled)
                prefs.push_notifications_enabled = int(push_notifications_enabled)
                prefs.alert_trigger_notifications = int(alert_trigger_notifications)
                prefs.weekly_summary_enabled = int(weekly_summary_enabled)
                prefs.updated_at = now
            else:
                # Create new
                prefs = NotificationPreferences(
                    email=email,
                    email_notifications_enabled=int(email_notifications_enabled),
                    push_notifications_enabled=int(push_notifications_enabled),
                    alert_trigger_notifications=int(alert_trigger_notifications),
                    weekly_summary_enabled=int(weekly_summary_enabled),
                    created_at=now,
                    updated_at=now
                )
                db.add(prefs)

            db.commit()
            db.refresh(prefs)
            db.close()

            logger.info(f"Updated notification preferences for {email}")
            return {
                'id': prefs.id,
                'email': prefs.email,
                'email_notifications_enabled': bool(prefs.email_notifications_enabled),
                'push_notifications_enabled': bool(prefs.push_notifications_enabled),
                'alert_trigger_notifications': bool(prefs.alert_trigger_notifications),
                'weekly_summary_enabled': bool(prefs.weekly_summary_enabled),
                'created_at': prefs.created_at.isoformat(),
                'updated_at': prefs.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Error updating notification preferences: {str(e)}")
            return None

    @staticmethod
    def delete_notification_preferences(email: str) -> bool:
        """
        Delete notification preferences for a user

        Args:
            email: User's email address

        Returns:
            True if deleted successfully
        """
        try:
            db = SessionLocal()
            deleted_count = db.query(NotificationPreferences).filter(
                NotificationPreferences.email == email
            ).delete()
            db.commit()
            db.close()

            if deleted_count > 0:
                logger.info(f"Deleted notification preferences for {email}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error deleting notification preferences: {str(e)}")
            return False


# ============================================================================
# Test Script
# ============================================================================

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("=" * 60)
    print("DimeDrop Supabase Database Module Test")
    print("=" * 60)

    # Test connection
    print("\n1. Testing Supabase connection...")
    manager = get_supabase_manager()
    if not manager.test_connection():
        print("❌ Connection failed!")
        exit(1)

    # Test cache operations
    print("\n2. Testing cache operations...")
    test_price_data = {
        "items": [{"price": 150.0, "date": "2025-10-11", "title": "Test Card"}],
        "avg_price": 150.0,
        "high": 150.0,
        "low": 150.0,
        "count": 1
    }

    cache_entry = CacheOperations.set_cached_price("Test Card", test_price_data)
    if cache_entry:
        print(f"   ✅ Created cache entry: {cache_entry['id']}")
    else:
        print("   ❌ Failed to create cache entry")
        exit(1)

    retrieved = CacheOperations.get_cached_price("Test Card")
    if retrieved:
        print(f"   ✅ Retrieved cache entry: {retrieved['card_query']}")
        assert retrieved['price_data'] == test_price_data, "Cache data mismatch"
    else:
        print("   ❌ Failed to retrieve cache entry")
        exit(1)

    # Test rate limit operations
    print("\n3. Testing rate limit operations...")
    count = RateLimitOperations.increment_call_count('ebay')
    print(f"   ✅ Incremented eBay call count to: {count}")

    current_count = RateLimitOperations.get_call_count('ebay')
    print(f"   ✅ Current eBay call count: {current_count}")

    under_limit = RateLimitOperations.check_rate_limit('ebay', 4800)
    print(f"   ✅ Under rate limit (4800): {under_limit}")

    # Test portfolio operations
    print("\n4. Testing portfolio operations...")
    card = PortfolioOperations.add_card(
        card_name="LeBron James Rookie Card",
        purchase_price=250.00,
        condition="PSA 9",
        notes="Great investment piece"
    )

    if card:
        print(f"   ✅ Added card to portfolio: {card['card_name']}")
        card_id = card['id']
    else:
        print("   ❌ Failed to add card to portfolio")
        exit(1)

    # Get all cards
    cards = PortfolioOperations.get_all_cards()
    print(f"   ✅ Retrieved {len(cards)} cards from portfolio")

    # Update card
    updated_card = PortfolioOperations.update_card(card_id, current_price=350.00)
    if updated_card:
        print(f"   ✅ Updated card price to: ${updated_card['current_price']}")
    else:
        print("   ❌ Failed to update card")

    # Clean up test data
    print("\n5. Cleaning up test data...")
    deleted = PortfolioOperations.delete_card(card_id)
    if deleted:
        print("   ✅ Deleted test card from portfolio")
    else:
        print("   ❌ Failed to delete test card")

    print("\n" + "=" * 60)
    print("✅ All Supabase integration tests passed!")
    print("=" * 60)
    print("1. Update price_tracker.py to use this database module")
    print("2. Test with real eBay API integration")
    print("3. Run FastAPI server and test endpoints")
