#!/usr/bin/env python3
"""
SQLAlchemy models for DimeDrop local SQLite database
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Text, DECIMAL, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class PriceCache(Base):
    """Price cache table for storing eBay price data"""
    __tablename__ = 'price_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_query = Column(String(255), nullable=False)
    price_data = Column(JSON, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_price_cache_card_query', 'card_query'),
        Index('idx_price_cache_expires_at', 'expires_at'),
    )

class ApiRateLimits(Base):
    """API rate limits table for tracking daily API usage"""
    __tablename__ = 'api_rate_limits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_name = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    call_count = Column(Integer, default=0)

    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

class Portfolio(Base):
    """Portfolio table for tracking user's card investments"""
    __tablename__ = 'portfolio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)  # Auth0 user ID
    card_name = Column(String(255), nullable=False)
    buy_price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    condition = Column(String(50))
    purchase_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_portfolio_user_id', 'user_id'),
        Index('idx_portfolio_card_name', 'card_name'),
        Index('idx_portfolio_created_at', 'created_at'),
    )

class Alert(Base):
    """Alerts table for price notification system"""
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)  # Auth0 user ID
    card_name = Column(String(255), nullable=False)
    target_price = Column(DECIMAL(10, 2), nullable=False)
    alert_type = Column(String(20), nullable=False)  # 'above' or 'below'
    is_active = Column(Integer, default=1)  # SQLite uses 0/1 for boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)
    notes = Column(Text)

    # Indexes
    __table_args__ = (
        Index('idx_alerts_user_id', 'user_id'),
        Index('idx_alerts_card_name', 'card_name'),
        Index('idx_alerts_is_active', 'is_active'),
        Index('idx_alerts_target_price', 'target_price'),
    )

class NotificationPreferences(Base):
    """User notification preferences"""
    __tablename__ = 'notification_preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    email_notifications_enabled = Column(Integer, default=1)  # Enable/disable email notifications
    push_notifications_enabled = Column(Integer, default=0)  # For future push notifications
    alert_trigger_notifications = Column(Integer, default=1)  # Price alert triggers
    weekly_summary_enabled = Column(Integer, default=0)  # Weekly portfolio summary
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_notification_preferences_email', 'email'),
    )

class TrackedListing(Base):
    """Tracked listings table for user-specific eBay item tracking"""
    __tablename__ = 'tracked_listings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)  # Auth0 user ID
    item_id = Column(String(50), nullable=False)  # eBay item ID
    card_name = Column(String(255), nullable=False)
    watch_count = Column(Integer, default=0)
    current_price = Column(DECIMAL(10, 2), nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_tracked_listings_user_id', 'user_id'),
        Index('idx_tracked_listings_item_id', 'item_id'),
        Index('idx_tracked_listings_end_time', 'end_time'),
    )

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./dimedrop.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == '__main__':
    # Create tables when run directly
    create_tables()
    print("✅ Database tables created successfully!")