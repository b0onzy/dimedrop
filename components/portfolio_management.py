"""
Portfolio Management component for DimeDrop Gradio app.
Handles user portfolio operations.
"""

import gradio as gr
import json
from datetime import datetime
import bleach


class PortfolioManagerComponent:
    """Portfolio management component with CRUD operations."""

    def __init__(self, api_manager):
        self.api = api_manager

    def update_portfolio(self, action, card_name, quantity):
        """Update portfolio with add/update/delete."""
        if not card_name.strip():
            return "❌ Please enter a card name."

        card_name = bleach.clean(card_name.strip())

        card_data = {
            "name": card_name,
            "quantity": quantity,
            "action": action.lower()
        }

        result = self.api.update_portfolio(action, card_data, "mock_token")

        if "error" in result:
            return f"❌ {result['error']}"

        return f"✅ {action}d {quantity} of '{card_name}' to portfolio."

    def get_portfolio(self):
        """Get current user portfolio."""
        return self.api.get_portfolio("mock_token")

    def export_portfolio(self, portfolio):
        """Export portfolio data."""
        return json.dumps({"portfolio": portfolio, "export_date": datetime.now().isoformat()}, indent=2)

    def render(self):
        """Render the portfolio management component content."""
        gr.Markdown("## Portfolio Management")
        gr.Markdown("*Stack your deck.*")

        with gr.Row():
            with gr.Column(scale=1):
                action_dropdown = gr.Dropdown(
                    ["Add", "Update", "Delete"],
                    label="Action",
                    value="Add"
                )
                portfolio_card_input = gr.Textbox(
                    label="Card Name",
                    placeholder="e.g., LeBron James Rookie"
                )
                quantity_input = gr.Number(
                    label="Quantity",
                    value=1,
                    minimum=1,
                    step=1
                )
                update_portfolio_btn = gr.Button("💾 Update Portfolio", variant="primary")

            with gr.Column(scale=2):
                portfolio_result = gr.Textbox(
                    label="Update Result",
                    interactive=False
                )
                portfolio_display = gr.JSON(label="Current Portfolio")
                export_button = gr.Button("📤 Export Portfolio")
                export_output = gr.Textbox(label="Exported Data", lines=10, interactive=False)

        update_portfolio_btn.click(
            self.update_portfolio,
            inputs=[action_dropdown, portfolio_card_input, quantity_input],
            outputs=portfolio_result
        ).then(
            self.get_portfolio,
            outputs=portfolio_display
        )

        export_button.click(
            self.export_portfolio,
            inputs=portfolio_display,
            outputs=export_output
        )

        # Load portfolio on component load
        # Note: This will be called when the component is rendered
