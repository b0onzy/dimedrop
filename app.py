"""
DimeDrop Gradio App - Professional Basketball Card Flipping Platform
Main entry point with collapsible side panel navigation.
"""

import gradio as gr
from components import (
    APIManager,
    HomeComponent,
    ScanCardComponent,
    PriceTrackerComponent,
    SentimentAnalyzerComponent,
    PortfolioManagerComponent
)
from theme import CUSTOM_CSS, dime_drop_theme


class DimeDropApp:
    """Main DimeDrop application with side panel navigation."""

    def __init__(self):
        self.api = APIManager()

        # Initialize components
        self.home = HomeComponent()
        self.scan_card = ScanCardComponent(self.api)
        self.price_tracker = PriceTrackerComponent(self.api)
        self.sentiment_analyzer = SentimentAnalyzerComponent(self.api)
        self.portfolio_manager = PortfolioManagerComponent(self.api)

    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface with collapsible side panel."""
        with gr.Blocks(title="DimeDrop - Flip Basketball Cards Like a Pro", css=CUSTOM_CSS) as app:

            # State management
            current_section = gr.State("home")  # Current active section
            sidebar_open = gr.State(True)  # Sidebar collapse state

            # Collapsible Side Panel
            with gr.Sidebar(
                label="",
                open=True,
                width=280,
                position="left",
                elem_classes="sidebar"
            ) as sidebar:
                # Brand Section
                with gr.Column(elem_classes="brand-section"):
                    gr.HTML("""
                    <div class="brand-logo">🏀 DimeDrop</div>
                    <div class="brand-tagline">Flip Cards Like a Pro</div>
                    """)

                # Navigation Section
                gr.Markdown("### Navigation")
                home_btn = gr.Button("🏠 Home", variant="secondary", size="lg", elem_classes="nav-button")
                scan_btn = gr.Button("📷 Scan Card", variant="secondary", size="lg", elem_classes="nav-button")
                price_btn = gr.Button("💰 Price Tracking", variant="secondary", size="lg", elem_classes="nav-button")
                sentiment_btn = gr.Button("🧠 Sentiment Analysis", variant="secondary", size="lg", elem_classes="nav-button")
                portfolio_btn = gr.Button("📊 Portfolio", variant="secondary", size="lg", elem_classes="nav-button")

                # Quick Stats Section
                with gr.Column(elem_classes="quick-stats"):
                    gr.Markdown("### Quick Stats")
                    with gr.Row(elem_classes="stat-item"):
                        gr.HTML('<div class="stat-label">Portfolio Value</div>')
                        gr.HTML('<div class="stat-value">$0.00</div>')

                    with gr.Row(elem_classes="stat-item"):
                        gr.HTML('<div class="stat-label">Cards Tracked</div>')
                        gr.HTML('<div class="stat-value">0</div>')

                    with gr.Row(elem_classes="stat-item"):
                        gr.HTML('<div class="stat-label">Active Alerts</div>')
                        gr.HTML('<div class="stat-value">0</div>')

            # Main content area with tabs for different sections
            with gr.Column(scale=4, elem_classes="main-content"):
                with gr.Tabs() as tabs:
                    # Home Tab
                    with gr.Tab("🏠 Home", id="home"):
                        self.home.render()

                    # Scan Card Tab
                    with gr.Tab("📷 Scan Card", id="scan"):
                        self.scan_card.render()

                    # Price Tracking Tab
                    with gr.Tab("💰 Price Tracking", id="price"):
                        self.price_tracker.render()

                    # Sentiment Analysis Tab
                    with gr.Tab("🧠 Sentiment Analysis", id="sentiment"):
                        self.sentiment_analyzer.render()

                    # Portfolio Management Tab
                    with gr.Tab("📊 Portfolio", id="portfolio"):
                        self.portfolio_manager.render()

            # Event handlers
            def switch_section(section_name):
                """Switch to a different section."""
                if section_name == "home":
                    return self.home.render()
                elif section_name == "scan":
                    return self.scan_card.render()
                elif section_name == "price":
                    return self.price_tracker.render()
                elif section_name == "sentiment":
                    return self.sentiment_analyzer.render()
                elif section_name == "portfolio":
                    return self.portfolio_manager.render()
                else:
                    return gr.Blocks().render()  # Empty block

            def toggle_sidebar():
                """Toggle sidebar visibility."""
                return gr.update(open=not sidebar_open.value)

            # Navigation button handlers - switch tabs
            home_btn.click(lambda: gr.Tabs(selected="home"), outputs=tabs)
            scan_btn.click(lambda: gr.Tabs(selected="scan"), outputs=tabs)
            price_btn.click(lambda: gr.Tabs(selected="price"), outputs=tabs)
            sentiment_btn.click(lambda: gr.Tabs(selected="sentiment"), outputs=tabs)
            portfolio_btn.click(lambda: gr.Tabs(selected="portfolio"), outputs=tabs)

        return app


def main():
    """Main entry point."""
    app_instance = DimeDropApp()
    app = app_instance.create_interface()

    # Launch with custom port
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False,
        favicon_path=None  # Add custom favicon if available
    )


if __name__ == "__main__":
    main()
import json
