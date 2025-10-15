"""
Price Tracking component for DimeDrop Gradio app.
Handles real-time price tracking for basketball cards.
"""

import gradio as gr
import bleach


class PriceTrackerComponent:
    """Price tracking component with card search and price display."""

    def __init__(self, api_manager):
        self.api = api_manager

    def get_price_data(self, card_name):
        """Get price data for a card."""
        if not card_name.strip():
            return {"error": "Please enter a card name."}

        # Sanitize input
        card_name = bleach.clean(card_name.strip())

        price_data = self.api.get_prices(card_name)
        return price_data

    def render(self):
        """Render the price tracking component content."""
        gr.Markdown("## Real-Time Price Tracking")
        gr.Markdown("*Track like a boss.*")

        card_name_input = gr.Textbox(
            label="Card Name",
            placeholder="e.g., Wembanyama Prizm",
            info="Enter the exact card name for best results"
        )
        price_button = gr.Button("📊 Get Price Data", variant="primary")
        price_result = gr.JSON(label="Price Information")

        price_button.click(
            self.get_price_data,
            inputs=[card_name_input],
            outputs=price_result
        )
