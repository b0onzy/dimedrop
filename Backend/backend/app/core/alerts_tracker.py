# DimeDrop Alerts Tracker
# Manages price alerts for basketball cards

import os
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging

# Import our database module
from .database import AlertOperations, NotificationOperations
from .notification_service import notification_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertsTracker:
    """Manages price alert operations"""

    def __init__(self):
        pass  # No database manager needed with Supabase

    async def create_alert(self, alert_data: Dict, user_id: Optional[str] = None) -> Dict:
        """
        Create a new price alert

        Args:
            alert_data: Dict containing card_name, target_price, alert_type
            user_id: Optional user ID for multi-user support

        Returns:
            Dict with alert details
        """
        try:
            # Validate required fields
            required_fields = ['card_name', 'target_price', 'alert_type']
            for field in required_fields:
                if field not in alert_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

            card_name = alert_data['card_name']
            target_price = float(alert_data['target_price'])
            alert_type = alert_data['alert_type']
            notes = alert_data.get('notes')

            if target_price <= 0:
                raise HTTPException(status_code=400, detail="Target price must be positive")

            if alert_type not in ['above', 'below']:
                raise HTTPException(status_code=400, detail="Alert type must be 'above' or 'below'")

            # Save to database
            alert_entry = AlertOperations.create_alert(
                card_name=card_name,
                target_price=target_price,
                alert_type=alert_type,
                notes=notes,
                user_id=user_id
            )

            if not alert_entry:
                raise HTTPException(status_code=500, detail="Failed to create alert")

            logger.info(f"Created alert for {card_name}: {alert_type} ${target_price}")

            return {
                'id': alert_entry['id'],
                'card_name': card_name,
                'target_price': target_price,
                'alert_type': alert_type,
                'is_active': True,
                'notes': notes,
                'created_at': alert_entry['created_at']
            }

        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

    async def get_alerts(self, active_only: bool = True, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get all alerts

        Args:
            active_only: If True, return only active alerts
            user_id: Optional user ID filter for multi-user support

        Returns:
            List of alert entries
        """
        try:
            alerts = AlertOperations.get_alerts(active_only=active_only, user_id=user_id)

            # Add current price information to each alert
            enriched_alerts = []
            for alert in alerts:
                current_price = self._get_current_price(alert['card_name'])
                alert_with_price = dict(alert)
                alert_with_price['current_price'] = current_price
                enriched_alerts.append(alert_with_price)

            return enriched_alerts

        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")

    async def update_alert(self, alert_id: int, update_data: Dict) -> Dict:
        """
        Update an existing alert

        Args:
            alert_id: ID of the alert to update
            update_data: Dict with fields to update

        Returns:
            Updated alert details
        """
        try:
            updated_alert = AlertOperations.update_alert(alert_id, update_data)

            if not updated_alert:
                raise HTTPException(status_code=404, detail="Alert not found")

            logger.info(f"Updated alert {alert_id}")

            return updated_alert

        except Exception as e:
            logger.error(f"Error updating alert: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating alert: {str(e)}")

    async def delete_alert(self, alert_id: int) -> bool:
        """
        Delete an alert

        Args:
            alert_id: ID of the alert to delete

        Returns:
            True if deleted successfully
        """
        try:
            success = AlertOperations.delete_alert(alert_id)

            if success:
                logger.info(f"Deleted alert {alert_id}")
            else:
                raise HTTPException(status_code=404, detail="Alert not found")

            return success

        except Exception as e:
            logger.error(f"Error deleting alert: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting alert: {str(e)}")

    async def check_alerts(self) -> List[Dict]:
        """
        Check all active alerts against current prices and return triggered alerts

        Returns:
            List of triggered alerts
        """
        try:
            alerts = await self.get_alerts(active_only=True)
            triggered_alerts = []

            for alert in alerts:
                current_price = alert['current_price']
                target_price = alert['target_price']
                alert_type = alert['alert_type']

                triggered = False
                if alert_type == 'above' and current_price >= target_price:
                    triggered = True
                elif alert_type == 'below' and current_price <= target_price:
                    triggered = True

                if triggered:
                    # Mark as triggered
                    await self.update_alert(alert['id'], {
                        'last_triggered': datetime.now(),
                        'is_active': False  # Deactivate after triggering
                    })

                    triggered_alert = {
                        'id': alert['id'],
                        'card_name': alert['card_name'],
                        'target_price': target_price,
                        'current_price': current_price,
                        'alert_type': alert_type,
                        'triggered_at': datetime.now()
                    }

                    triggered_alerts.append(triggered_alert)

                    # Send notification if user has preferences set up
                    await self._send_alert_notification(triggered_alert)

            return triggered_alerts

        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error checking alerts: {str(e)}")

    async def _send_alert_notification(self, alert_data: Dict) -> None:
        """
        Send notification for triggered alert

        Args:
            alert_data: Triggered alert data
        """
        try:
            # Get user's notification preferences
            # For now, we'll use a default email - in production this would be user-specific
            default_email = os.getenv('DEFAULT_USER_EMAIL', 'chaisincardboard@gmail.com')

            prefs = NotificationOperations.get_notification_preferences(default_email)

            if prefs and prefs.get('email_notifications_enabled', True) and prefs.get('alert_trigger_notifications', True):
                # Send email notification
                success = await notification_service.send_price_alert_notification(
                    user_email=default_email,
                    alert_data={
                        'card_name': alert_data['card_name'],
                        'target_price': alert_data['target_price'],
                        'condition': alert_data['alert_type']
                    },
                    current_price=alert_data['current_price']
                )

                if success:
                    logger.info(f"Sent notification for triggered alert: {alert_data['card_name']}")
                else:
                    logger.warning(f"Failed to send notification for alert: {alert_data['card_name']}")
            else:
                logger.info(f"Notifications disabled or not configured for alert: {alert_data['card_name']}")

        except Exception as e:
            logger.error(f"Error sending alert notification: {str(e)}")
            # Don't raise exception - notification failure shouldn't break alert checking

    def _get_current_price(self, card_name: str) -> float:
        """
        Get current price for a card (mock implementation)

        In production, this would call the price tracker
        """
        # Mock price logic - in production this would call the actual price tracker
        # For now, return a mock price based on card name
        base_prices = {
            'Wembanyama Prizm': 152.50,
            'Luka Doncic Auto': 200.00,
            'LeBron James': 85.00,
            'Stephen Curry': 120.00
        }

        # Return base price or a default
        return base_prices.get(card_name, 100.00)