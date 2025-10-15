# DimeDrop Portfolio Tracker
# Manages user's basketball card collection and ROI calculations

import os
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging

# Import our database module
from .database import PortfolioOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioTracker:
    """Manages user portfolio operations"""

    def __init__(self):
        pass  # No database manager needed with Supabase

    async def add_card_to_portfolio(self, card_data: Dict, user_id: Optional[str] = None) -> Dict:
        """
        Add a card to the user's portfolio

        Args:
            card_data: Dict containing card_name, buy_price, quantity, condition (optional)
            user_id: Optional user ID for multi-user support

        Returns:
            Dict with portfolio entry details and ROI calculation
        """
        try:
            # Validate required fields
            required_fields = ['card_name', 'buy_price', 'quantity']
            for field in required_fields:
                if field not in card_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

            card_name = card_data['card_name']
            buy_price = float(card_data['buy_price'])
            quantity = int(card_data['quantity'])
            condition = card_data.get('condition', 'Raw')
            purchase_date = card_data.get('purchase_date')
            notes = card_data.get('notes')

            if buy_price <= 0 or quantity <= 0:
                raise HTTPException(status_code=400, detail="Buy price and quantity must be positive")

            # Get current price from price tracker (mock for now)
            # In production, this would call the price tracker
            current_price = self._get_current_price(card_name)

            # Calculate ROI
            total_investment = buy_price * quantity
            current_value = current_price * quantity
            roi_percentage = ((current_value - total_investment) / total_investment) * 100

            # Save to database
            portfolio_entry = PortfolioOperations.add_card(
                card_name=card_name,
                purchase_price=buy_price,
                quantity=quantity,
                condition=condition,
                purchase_date=purchase_date,
                notes=notes,
                user_id=user_id
            )

            if not portfolio_entry:
                raise HTTPException(status_code=500, detail="Failed to save card to portfolio")

            logger.info(f"Added {card_name} to portfolio: {quantity} cards at ${buy_price} each")

            return {
                'id': portfolio_entry['id'],
                'card_name': card_name,
                'buy_price': buy_price,
                'current_price': current_price,
                'quantity': quantity,
                'condition': condition,
                'total_investment': total_investment,
                'current_value': current_value,
                'roi_percentage': round(roi_percentage, 2),
                'created_at': portfolio_entry['created_at']
            }

        except Exception as e:
            logger.error(f"Error adding card to portfolio: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding card to portfolio: {str(e)}")

    async def get_portfolio(self, user_id: Optional[str] = None) -> List[Dict]:
        """
        Get user's portfolio entries

        Args:
            user_id: Optional user ID filter (for future multi-user support)

        Returns:
            List of portfolio entries with current prices and ROI
        """
        try:
            entries = PortfolioOperations.get_all_cards(user_id=user_id)

            portfolio = []
            for entry in entries:
                # Get current price (mock for now)
                current_price = self._get_current_price(entry['card_name'])

                # Recalculate ROI with current price
                total_investment = (entry['buy_price'] or 0) * entry['quantity']
                current_value = current_price * entry['quantity']
                roi_percentage = ((current_value - total_investment) / total_investment) * 100 if total_investment > 0 else 0

                portfolio.append({
                    'id': entry['id'],
                    'card_name': entry['card_name'],
                    'buy_price': entry['buy_price'] or 0,
                    'current_price': current_price,
                    'quantity': entry['quantity'],
                    'condition': entry['condition'] or 'Raw',
                    'total_investment': total_investment,
                    'current_value': current_value,
                    'roi_percentage': round(roi_percentage, 2),
                    'purchase_date': entry['purchase_date'],
                    'created_at': entry['created_at']
                })

            return portfolio

        except Exception as e:
            logger.error(f"Error retrieving portfolio: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving portfolio: {str(e)}")

    async def export_portfolio_csv(self, user_id: Optional[str] = None) -> str:
        """
        Export portfolio as CSV string

        Returns:
            CSV formatted string of portfolio data
        """
        try:
            portfolio = await self.get_portfolio(user_id)

            if not portfolio:
                return "No portfolio data available"

            # CSV header
            csv_lines = [
                "Card Name,Buy Price,Current Price,Quantity,Condition,Total Investment,Current Value,ROI %,Purchase Date"
            ]

            # CSV data rows
            for entry in portfolio:
                line = ",".join([
                    entry['card_name'],
                    str(entry['buy_price']),
                    str(entry['current_price']),
                    str(entry['quantity']),
                    entry['condition'],
                    str(entry['total_investment']),
                    str(entry['current_value']),
                    str(entry['roi_percentage']),
                    entry['purchase_date'] or ''
                ])
                csv_lines.append(line)

            return "\n".join(csv_lines)

        except Exception as e:
            logger.error(f"Error exporting portfolio CSV: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error exporting portfolio: {str(e)}")

    def _get_current_price(self, card_name: str) -> float:
        """
        Get current market price for a card
        In production, this would call the price tracker API
        For now, returns mock prices based on card name
        """
        # Mock price logic - in production, call price tracker
        card_lower = card_name.lower()

        if 'wembanyama' in card_lower:
            return 152.50
        elif 'lebron' in card_lower:
            return 48.90
        elif 'jordan' in card_lower:
            return 125.00
        else:
            return 35.00  # Default price for unknown cards


# Global instance for use in FastAPI
portfolio_tracker = PortfolioTracker()


# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def test_portfolio():
        # Test adding a card
        card_data = {
            'card_name': 'Wembanyama Prizm',
            'buy_price': 120.0,
            'quantity': 2,
            'condition': 'PSA 10'
        }

        result = await portfolio_tracker.add_card_to_portfolio(card_data)
        print(f"Added to portfolio: {result}")

        # Test getting portfolio
        portfolio = await portfolio_tracker.get_portfolio()
        print(f"Portfolio: {portfolio}")

        # Test CSV export
        csv_data = await portfolio_tracker.export_portfolio_csv()
        print(f"CSV Export:\n{csv_data}")

    asyncio.run(test_portfolio())