# DimeDrop FastAPI Application
# Main entry point for the API server

from fastapi import FastAPI, HTTPException, Query, Response, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from both ~/.env and config/.env
from backend.app.utils.load_env import load_environment
load_environment()

# Initialize Supabase (no explicit init needed - handled by database module)
# Supabase handles schema automatically via migrations

# Import our modules
from backend.app.core.price_tracker import get_card_prices_endpoint
# from backend.app.core.sentiment_analyzer import SentimentAnalyzer
from backend.app.core.sentiment_analyzer import SentimentAnalyzer
# from backend.app.core.forecast_model import ForecastModel
from backend.app.core.portfolio_tracker import PortfolioTracker
from backend.app.core.alerts_tracker import AlertsTracker
from backend.app.core.vision_processor import VisionProcessor
from backend.app.core.database import NotificationOperations
from backend.app.core.notification_service import notification_service
from backend.app.services.auth import get_current_user, get_optional_user
from backend.app.api.upload_card import router as upload_card_router
from backend.app.api.ebay import router as ebay_router

# Initialize components
# forecast_model = ForecastModel()
sentiment_analyzer = SentimentAnalyzer()
portfolio_tracker = PortfolioTracker()
alerts_tracker = AlertsTracker()
vision_processor = VisionProcessor()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DimeDrop API",
    description="Basketball card flipping automation API with eBay price tracking, sentiment analysis, and portfolio management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#     allow_origins=["*"],  # In production, specify actual origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include API routers
app.include_router(upload_card_router, prefix="/api", tags=["upload"])
app.include_router(ebay_router, prefix="/api", tags=["ebay"])

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI server starting up")
    if not os.getenv("EBAY_APP_ID"):
        logger.error("EBAY_APP_ID not set")
        raise ValueError("EBAY_APP_ID environment variable required")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "DimeDrop API",
        "version": "1.0.0",
        "endpoints": {
            "prices": "/prices?card={query}",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    # Check if credentials look like real values (not placeholders)
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
    news_key = os.getenv('NEWS_API_KEY')
    
    reddit_configured = (
        reddit_id and reddit_secret and
        not reddit_id.startswith('placeholder') and
        not reddit_secret.startswith('placeholder') and
        len(reddit_id) > 10 and len(reddit_secret) > 10
    )
    
    news_configured = (
        news_key and
        not news_key.startswith('placeholder') and
        len(news_key) > 10
    )
    
    return {
        "status": "healthy",
        "database": "connected" if os.getenv('DATABASE_URL') else "not configured",
        "ebay_api": "configured" if os.getenv('EBAY_APP_ID') else "not configured",
        "reddit_api": "configured" if reddit_configured else "not configured",
        "news_api": "configured" if news_configured else "not configured"
    }


@app.get("/prices")
async def get_prices(
    card: str = Query(
        ...,
        min_length=3,
        description="Basketball card search query (e.g., 'Wembanyama Prizm')",
        examples=[{"value": "Wembanyama Prizm"}]
    )
):
    """
    Get eBay price data for basketball cards

    - **card**: Search query for the card (minimum 3 characters)

    Returns:
    - items: List of recent sold listings
    - avg_price: Average price
    - high: Highest price
    - low: Lowest price
    - count: Number of listings
    - cached: Whether data is from cache
    - cache_date: When data was cached

    **Caching**: Price data is cached for up to 90 days (eBay ToS compliance)

    **Rate Limiting**: Max 4,800 calls/day (buffer for 5K eBay limit)
    """
    try:
        # Mock response for testing
        return {
            "card": card,
            "avg_price": 152.50,
            "high": 160.0,
            "low": 145.0,
            "count": 5,
            "cached": False,
            "cache_date": None,
            "mock_data": True
        }
    except Exception as e:
        # logger.error(f"Error in /prices endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/prices/{card_name}")
async def get_prices_by_path(card_name: str):
    """
    Alternative endpoint: Get prices by path parameter

    Example: /prices/Wembanyama-Prizm
    """
    # Replace dashes with spaces
    card_query = card_name.replace('-', ' ')
    return await get_prices(card=card_query)


@app.get("/sentiment/{card_name}")
async def get_sentiment(card_name: str):
    """
    Get sentiment analysis and Flip Score for a basketball card
    """
    try:
        # Initialize sentiment analyzer
        analyzer = SentimentAnalyzer()
        
        # Get sentiment analysis
        result = await analyzer.analyze_card_sentiment(card_name)
        
        return result
    except Exception as e:
        # logger.error(f"Error in /sentiment endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error performing sentiment analysis")


# @app.get("/forecast/{card_name}")
# async def get_forecast(
#     card_name: str,
#     days: int = Query(7, ge=1, le=30, description="Number of days to forecast ahead")
# ):
#     """
#     Get price forecast for a basketball card using machine learning

#     - **card_name**: Name of the basketball card
#     - **days**: Number of days to forecast (1-30, default 7)

#     Returns:
#     - card_name: Card name
#     - current_price: Current average price
#     - predictions: List of daily predictions with dates and prices
#     - trend: Overall trend (bullish/bearish/stable)
#     - confidence_level: Model confidence
#     - forecast_period: Time period of forecast
#     - model_accuracy: Whether model is trained
#     """
#     try:
#         # Get current price data for the card
#         current_data = await get_card_prices_endpoint(card_name)
#         current_price = current_data.get('avg_price', 150.0)
        
#         # Create mock historical data for training (in production, this would come from database)
#         base_price = current_price
#         historical_data = []
#         for i in range(15):  # Need at least 10 points
#             date = (datetime.now() - timedelta(days=15-i)).strftime('%Y-%m-%d')
#             # Create a gradual upward trend
#             price = base_price * (0.85 + (i * 0.01))
#             historical_data.append({"date": date, "price": round(price, 2)})
        
#         # Train and predict
#         price_data = [item['price'] for item in historical_data]
#         forecast_result = forecast_model.predict_price(price_data)
        
#         return forecast_result

#     except Exception as e:
#         # logger.error(f"Error in /forecast endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error generating price forecast")


@app.get("/portfolio")
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    """
    Get user's basketball card portfolio with current prices and ROI calculations

    Returns:
    - portfolio: List of cards with current values and ROI
    - total_investment: Total amount invested
    - total_value: Current total value
    - total_roi: Overall ROI percentage
    """
    try:
        tracker = PortfolioTracker()
        user_id = current_user.get('sub') if current_user else None
        portfolio = await tracker.get_portfolio(user_id=user_id)
        
        # Calculate totals
        total_investment = sum(card['total_investment'] for card in portfolio)
        total_value = sum(card['current_value'] for card in portfolio)
        total_roi = ((total_value - total_investment) / total_investment) * 100 if total_investment > 0 else 0
        
        return {
            "portfolio": portfolio,
            "summary": {
                "total_investment": round(total_investment, 2),
                "total_value": round(total_value, 2),
                "total_roi_percentage": round(total_roi, 2),
                "card_count": len(portfolio)
            }
        }
    except Exception as e:
        # logger.error(f"Error in /portfolio endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving portfolio")


@app.post("/portfolio")
async def add_to_portfolio(
    card_name: str = Query(..., description="Name of the basketball card"),
    purchase_price: float = Query(..., gt=0, description="Purchase price per card"),
    quantity: int = Query(1, gt=0, description="Number of cards purchased"),
    condition: str = Query(None, description="Card condition (e.g., 'PSA 10', 'Raw')"),
    purchase_date: str = Query(None, description="Purchase date (YYYY-MM-DD)"),
    notes: str = Query(None, description="Optional notes about the purchase"),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a card to the user's portfolio

    - **card_name**: Name of the basketball card
    - **purchase_price**: Price paid per card
    - **quantity**: Number of cards (default 1)
    - **condition**: Card condition/grade
    - **purchase_date**: Date of purchase (YYYY-MM-DD)
    - **notes**: Optional purchase notes

    Returns the added card details
    """
    try:
        from datetime import datetime
        
        # Parse purchase date if provided
        parsed_date = None
        if purchase_date:
            try:
                parsed_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Prepare card data
        card_data = {
            'card_name': card_name,
            'buy_price': purchase_price,
            'quantity': quantity,
            'condition': condition or 'Raw',
            'purchase_date': parsed_date,
            'notes': notes
        }
        
        tracker = PortfolioTracker()
        user_id = current_user.get('sub') if current_user else None
        result = await tracker.add_card_to_portfolio(card_data, user_id=user_id)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        # logger.error(f"Error in POST /portfolio endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding card to portfolio")


@app.get("/portfolio/export")
async def export_portfolio_csv():
    """
    Export user's portfolio as CSV for tax purposes

    Returns:
        CSV formatted string of portfolio data
    """
    try:
        tracker = PortfolioTracker()
        csv_data = await tracker.export_portfolio_csv()

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=portfolio.csv"}
        )
    except Exception as e:
        # logger.error(f"Error in /portfolio/export endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error exporting portfolio")


@app.get("/alerts")
async def get_alerts(
    active_only: bool = Query(True, description="Return only active alerts"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all price alerts

    - **active_only**: If true, return only active alerts (default: true)

    Returns:
        List of alerts with current prices
    """
    try:
        user_id = current_user.get('sub') if current_user else None
        alerts = await alerts_tracker.get_alerts(active_only=active_only, user_id=user_id)
        return {"alerts": alerts}
    except Exception as e:
        # logger.error(f"Error in /alerts endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving alerts")


@app.post("/alerts")
async def create_alert(
    card_name: str = Query(..., description="Name of the basketball card"),
    target_price: float = Query(..., gt=0, description="Target price for the alert"),
    alert_type: str = Query(..., description="Alert type: 'above' or 'below'"),
    notes: str = Query(None, description="Optional notes for the alert"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new price alert

    - **card_name**: Name of the basketball card
    - **target_price**: Price threshold for the alert
    - **alert_type**: 'above' (notify when price goes above target) or 'below' (notify when price goes below target)
    - **notes**: Optional notes

    Returns the created alert details
    """
    try:
        alert_data = {
            'card_name': card_name,
            'target_price': target_price,
            'alert_type': alert_type,
            'notes': notes
        }

        user_id = current_user.get('sub') if current_user else None
        result = await alerts_tracker.create_alert(alert_data, user_id=user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        # logger.error(f"Error in POST /alerts endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating alert")


@app.put("/alerts/{alert_id}")
async def update_alert(
    alert_id: int,
    card_name: str = Query(None, description="Updated card name"),
    target_price: float = Query(None, gt=0, description="Updated target price"),
    alert_type: str = Query(None, description="Updated alert type"),
    is_active: bool = Query(None, description="Whether alert is active"),
    notes: str = Query(None, description="Updated notes")
):
    """
    Update an existing alert

    - **alert_id**: ID of the alert to update
    - **card_name**: Updated card name (optional)
    - **target_price**: Updated target price (optional)
    - **alert_type**: Updated alert type (optional)
    - **is_active**: Whether alert is active (optional)
    - **notes**: Updated notes (optional)

    Returns the updated alert details
    """
    try:
        update_data = {}
        if card_name is not None:
            update_data['card_name'] = card_name
        if target_price is not None:
            update_data['target_price'] = target_price
        if alert_type is not None:
            update_data['alert_type'] = alert_type
        if is_active is not None:
            update_data['is_active'] = is_active
        if notes is not None:
            update_data['notes'] = notes

        result = await alerts_tracker.update_alert(alert_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Alert not found")

        return result
    except HTTPException:
        raise
    except Exception as e:
        # logger.error(f"Error in PUT /alerts endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating alert")


@app.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int):
    """
    Delete a price alert

    - **alert_id**: ID of the alert to delete

    Returns success confirmation
    """
    try:
        success = await alerts_tracker.delete_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {"message": "Alert deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        # logger.error(f"Error in DELETE /alerts endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting alert")


@app.post("/alerts/check")
async def check_alerts():
    """
    Manually check all active alerts against current prices

    Returns list of triggered alerts
    """
    try:
        triggered_alerts = await alerts_tracker.check_alerts()
        return {"triggered_alerts": triggered_alerts}
    except Exception as e:
        # logger.error(f"Error in POST /alerts/check endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking alerts")


# ============================================================================
# Notification Endpoints
# ============================================================================

@app.get("/notifications/preferences")
async def get_notification_preferences(email: str = Query(..., description="User email address")):
    """Get notification preferences for a user"""
    try:
        prefs = NotificationOperations.get_notification_preferences(email)
        if not prefs:
            raise HTTPException(status_code=404, detail="Notification preferences not found")
        return prefs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notification preferences: {str(e)}")


@app.post("/notifications/preferences")
async def update_notification_preferences(preferences: dict):
    """
    Create or update notification preferences for a user

    Expected JSON:
    {
        "email": "user@example.com",
        "email_notifications_enabled": true,
        "push_notifications_enabled": false,
        "alert_trigger_notifications": true,
        "weekly_summary_enabled": false
    }
    """
    try:
        required_fields = ['email']
        for field in required_fields:
            if field not in preferences:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        email = preferences['email']
        email_enabled = preferences.get('email_notifications_enabled', True)
        push_enabled = preferences.get('push_notifications_enabled', False)
        alert_notifications = preferences.get('alert_trigger_notifications', True)
        weekly_summary = preferences.get('weekly_summary_enabled', False)

        result = NotificationOperations.create_or_update_notification_preferences(
            email=email,
            email_notifications_enabled=email_enabled,
            push_notifications_enabled=push_enabled,
            alert_trigger_notifications=alert_notifications,
            weekly_summary_enabled=weekly_summary
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to update notification preferences")

        return {"message": "Notification preferences updated successfully", "preferences": result}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification preferences: {str(e)}")


@app.post("/notifications/test")
async def send_test_notification(email: str):
    """Send a test notification to verify email setup"""
    try:
        success = await notification_service.send_test_notification(email)
        if success:
            return {"message": "Test notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test notification")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending test notification: {str(e)}")


@app.delete("/notifications/preferences")
async def delete_notification_preferences(email: str = Query(..., description="User email address")):
    """Delete notification preferences for a user"""
    try:
        success = NotificationOperations.delete_notification_preferences(email)
        if not success:
            raise HTTPException(status_code=404, detail="Notification preferences not found")
        return {"message": "Notification preferences deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification preferences: {str(e)}")


@app.post("/vision/scan")
async def scan_card_image(file: UploadFile = File(...)):
    """Upload card image for AI processing and auto-add to portfolio"""
    processor = VisionProcessor()
    result = await processor.process_card_image(file)
    
    # Auto-add to portfolio with detected details
    portfolio_data = {
        'card_name': result['card_name'],
        'buy_price': result['current_price'],  # Assume current market
        'quantity': 1,
        'condition': result['condition']
    }
    
    tracker = PortfolioTracker()
    add_result = await tracker.add_card_to_portfolio(portfolio_data)
    
    return {
        'vision_result': result,
        'portfolio_entry': add_result,
        'message': f"Auto-added {result['card_name']} to portfolio!"
    }


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on localhost:8000")
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.critical(f"Server crashed: {str(e)}", exc_info=True)
        raise
