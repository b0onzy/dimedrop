# DimeDrop Notification Service
# Handles email and push notifications for price alerts

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Template
import json

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending notifications for triggered alerts"""

    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'chaisincardboard@gmail.com')
        self.app_url = os.getenv('APP_URL', 'http://localhost:3002')

        # Initialize SendGrid client if API key is available
        self.sendgrid_client = None
        if self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
        else:
            logger.warning("SendGrid API key not found - email notifications disabled")

    async def send_price_alert_notification(
        self,
        user_email: str,
        alert_data: Dict,
        current_price: float
    ) -> bool:
        """
        Send email notification for triggered price alert

        Args:
            user_email: User's email address
            alert_data: Alert details from database
            current_price: Current market price that triggered the alert

        Returns:
            bool: True if notification sent successfully
        """
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured - skipping email notification")
            return False

        try:
            # Create email content
            subject = f"🎯 Price Alert Triggered: {alert_data['card_name']}"

            # HTML template for the email
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Price Alert Triggered</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #1a365d; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                    .content { background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; }
                    .alert-details { background: white; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #e53e3e; }
                    .price-info { display: flex; justify-content: space-between; margin: 10px 0; }
                    .cta-button { display: inline-block; background: #3182ce; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 Price Alert Triggered!</h1>
                        <p>Your DimeDrop alert has been activated</p>
                    </div>
                    <div class="content">
                        <h2>{{ card_name }}</h2>

                        <div class="alert-details">
                            <h3>Alert Details</h3>
                            <div class="price-info">
                                <span><strong>Target Price:</strong> ${{ "%.2f"|format(target_price) }}</span>
                                <span><strong>Condition:</strong> {{ condition.title() }}</span>
                            </div>
                            <div class="price-info">
                                <span><strong>Current Price:</strong> ${{ "%.2f"|format(current_price) }}</span>
                                <span><strong>Triggered:</strong> {{ triggered_at.strftime('%Y-%m-%d %H:%M') }}</span>
                            </div>
                        </div>

                        <p>Great news! The price of <strong>{{ card_name }}</strong> has {{ "risen above" if condition == "above" else "fallen below" }} your target price of ${{ "%.2f"|format(target_price) }}.</p>

                        <p>Current market price: <strong>${{ "%.2f"|format(current_price) }}</strong></p>

                        <div style="text-align: center;">
                            <a href="{{ app_url }}/alerts" class="cta-button">View All Alerts</a>
                        </div>

                        <p>You can manage your alerts and portfolio at <a href="{{ app_url }}">{{ app_url }}</a></p>

                        <div class="footer">
                            <p>This alert was triggered by DimeDrop's price monitoring system.</p>
                            <p>To unsubscribe from alerts, visit your <a href="{{ app_url }}/settings">account settings</a>.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Render template
            template = Template(html_template)
            html_content = template.render(
                card_name=alert_data['card_name'],
                target_price=alert_data['target_price'],
                condition=alert_data['condition'],
                current_price=current_price,
                triggered_at=datetime.now(),
                app_url=self.app_url
            )

            # Create email
            from_email = Email(self.from_email)
            to_email = To(user_email)
            content = Content("text/html", html_content)
            mail = Mail(from_email, to_email, subject, content)

            # Send email
            response = self.sendgrid_client.send(mail)

            if response.status_code == 202:
                logger.info(f"Price alert notification sent to {user_email} for {alert_data['card_name']}")
                return True
            else:
                logger.error(f"Failed to send email notification: {response.status_code} - {response.body}")
                return False

        except Exception as e:
            logger.error(f"Error sending price alert notification: {str(e)}")
            return False

    async def send_test_notification(self, user_email: str) -> bool:
        """Send a test notification to verify email setup"""
        if not self.sendgrid_client:
            logger.warning("SendGrid not configured - cannot send test notification")
            return False

        try:
            subject = "🧪 DimeDrop Test Notification"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Test Notification</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #1a365d;">🧪 Test Notification</h1>
                    <p>This is a test notification from DimeDrop to verify your email settings are working correctly.</p>
                    <p>If you received this email, your notification system is properly configured!</p>
                    <p><a href="{self.app_url}" style="color: #3182ce;">Visit DimeDrop</a></p>
                    <hr>
                    <p style="font-size: 12px; color: #666;">Sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """

            from_email = Email(self.from_email)
            to_email = To(user_email)
            content = Content("text/html", html_content)
            mail = Mail(from_email, to_email, subject, content)

            response = self.sendgrid_client.send(mail)

            if response.status_code == 202:
                logger.info(f"Test notification sent to {user_email}")
                return True
            else:
                logger.error(f"Failed to send test notification: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending test notification: {str(e)}")
            return False


# Global notification service instance
notification_service = NotificationService()