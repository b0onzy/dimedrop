"""
UI Components for DimeDrop
Main Gradio interface and UI logic.
"""

import json
import bleach
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import gradio as gr

from .auth import AuthManager
from .api import APIManager


# Custom CSS
CUSTOM_CSS = """
:root {
    --primary-color: #F97316;
    --secondary-color: #EA580C;
    --background-dark: #1A1A1A;
    --background-card: #2A2A2A;
    --text-light: #FFFFFF;
    --text-muted: #9CA3AF;
    --border-color: #F97316;
}

.gradio-container {
    font-family: 'Inter', sans-serif;
    background: var(--background-dark);
    color: var(--text-light);
}

.sidebar {
    background: var(--background-card);
    border-right: 2px solid var(--border-color);
    padding: 20px;
    min-height: 100vh;
    box-shadow: 2px 0 8px rgba(249, 115, 22, 0.1);
}

.main-content {
    padding: 20px;
    background: var(--background-dark);
}

.tab-content {
    padding: 20px;
    background: var(--background-dark);
    border-radius: 10px;
    margin: 10px 0;
}

.hero-section {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
    color: white;
    border-radius: 15px;
    margin-bottom: 30px;
}

.feature-card {
    background: var(--background-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    transition: transform 0.2s;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.btn-primary {
    background: var(--primary-color) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
}

.btn-primary:hover {
    background: var(--secondary-color) !important;
}

.auth-badge {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
}

@media (max-width: 768px) {
    .sidebar {
        position: static;
        border-right: none;
        border-bottom: 2px solid var(--border-color);
        min-height: auto;
        padding: 15px;
    }
    .main-content {
        padding: 15px;
    }
    .gradio-container {
        flex-direction: column;
    }
}
"""


class DimeDropApp:
    """Main DimeDrop Gradio application."""

    def __init__(self):
        self.auth = AuthManager()
        self.api = APIManager()
        self.current_user = None
        self.current_token = None

    def authenticate_user(self, token: str) -> Tuple[bool, str]:
        """Authenticate user with JWT token."""
        payload = self.auth.validate_jwt(token)
        if payload:
            self.current_user = payload
            self.current_token = token
            return True, f"Welcome back, {payload.get('name', 'User')}!"
        return False, "Invalid authentication token."

    def logout_user(self) -> Tuple[None, str]:
        """Logout current user."""
        self.current_user = None
        self.current_token = None
        return None, "Logged out successfully."

    def preprocess_image(self, image) -> Optional[bytes]:
        """Preprocess image for scanning."""
        if image is None:
            return None
        # Convert PIL to bytes
        import io
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def scan_card_interface(self, image) -> str:
        """Handle card scanning interface."""
        if not self.current_token:
            return "❌ Please login to use this feature."

        if image is None:
            return "❌ Please upload a card image."

        img_bytes = self.preprocess_image(image)
        if not img_bytes:
            return "❌ Failed to process image."

        result = self.api.scan_card(img_bytes, self.current_token)

        if "error" in result:
            return f"⚠️ {result['error']}\nMock Result: LeBron James Rookie Card (92% confidence)"

        return f"✅ Card identified: {result.get('card_name', 'Unknown')}\nConfidence: {result.get('confidence', 0)*100:.1f}%"

    def get_price_interface(self, card_name: str) -> Dict:
        """Handle price tracking interface."""
        if not card_name.strip():
            return {"error": "Please enter a card name."}

        # Sanitize input
        card_name = bleach.clean(card_name.strip())

        price_data = self.api.get_prices(card_name)
        return price_data

    def analyze_sentiment_interface(self, text: str) -> Dict:
        """Handle sentiment analysis interface."""
        if not text.strip():
            return {"error": "Please enter text to analyze."}

        # For demo, analyze the text directly
        # In production, this would call the API
        positive_words = ['bullish', 'up', 'rise', 'increase', 'positive', 'good', 'profit']
        negative_words = ['bearish', 'down', 'fall', 'decrease', 'negative', 'bad', 'loss']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        flip_score = min(100, max(0, 50 + (positive_count - negative_count) * 10))

        return {
            "flip_score": flip_score,
            "sentiment_breakdown": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": max(0, len(text.split()) - positive_count - negative_count)
            }
        }

    def update_portfolio_interface(self, action: str, card_name: str, quantity: int) -> str:
        """Handle portfolio update interface."""
        if not self.current_token:
            return "❌ Please login to use this feature."

        if not card_name.strip():
            return "❌ Please enter a card name."

        card_name = bleach.clean(card_name.strip())

        card_data = {
            "name": card_name,
            "quantity": quantity,
            "action": action.lower()
        }

        result = self.api.update_portfolio(action, card_data, self.current_token)

        if "error" in result:
            return f"❌ {result['error']}"

        return f"✅ {action}d {quantity} of '{card_name}' to portfolio."

    def get_portfolio_interface(self) -> List[Dict]:
        """Get current user portfolio."""
        if not self.current_token:
            return []

        return self.api.get_portfolio(self.current_token)

    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface with improved layout."""
        with gr.Blocks(title="DimeDrop - Flip Basketball Cards Like a Pro", css=CUSTOM_CSS) as app:

            # State management
            auth_state = gr.State(None)  # JWT token
            user_state = gr.State(None)  # User info
            current_tab = gr.State("Home")

            # Professional Sidebar Navigation
            with gr.Sidebar(
                label="DimeDrop Navigation",
                open=True,
                width=280,
                position="left",
                elem_classes="sidebar"
            ) as sidebar:
                gr.Markdown("# 🏀 DimeDrop")
                gr.Markdown("*Flip Basketball Cards Like a Pro*")

                # User status section
                with gr.Group():
                    gr.Markdown("### 👤 User Status")
                    auth_status = gr.Textbox(
                        label="Status",
                        value="Not logged in",
                        interactive=False,
                        lines=1
                    )
                    login_btn = gr.Button("🔐 Login with Google", variant="primary", size="sm")
                    logout_btn = gr.Button("🚪 Logout", variant="secondary", size="sm", visible=False)

                gr.Markdown("---")

                # Navigation section
                gr.Markdown("### 🧭 Navigation")
                home_btn = gr.Button("🏠 Home", variant="secondary", size="lg")
                scan_btn = gr.Button("📷 Scan Card", variant="secondary", size="lg")
                price_btn = gr.Button("💰 Price Tracking", variant="secondary", size="lg")
                sentiment_btn = gr.Button("🧠 Sentiment Analysis", variant="secondary", size="lg")
                portfolio_btn = gr.Button("📊 Portfolio", variant="secondary", size="lg")

                gr.Markdown("---")

                # Quick stats section
                gr.Markdown("### 📈 Quick Stats")
                with gr.Group():
                    gr.Textbox(
                        label="Portfolio Value",
                        value="$0.00",
                        interactive=False,
                        lines=1
                    )
                    gr.Textbox(
                        label="Cards Tracked",
                        value="0",
                        interactive=False,
                        lines=1
                    )

            # Main content area with improved tabs
            with gr.Column(scale=4, elem_classes="main-content"):
                # Enhanced tab system
                with gr.Tabs(selected="home") as tabs:
                    # Home Tab
                    with gr.Tab("🏠 Home", id="home"):
                        with gr.Column():
                            gr.HTML("""
                            <div class="hero-section">
                                <h1>DimeDrop</h1>
                                <h2>Flip Basketball Cards Like a Pro</h2>
                                <p>Your Cards, Your Data, Your Profits</p>
                                <p style="font-style: italic;">Ready to dominate the court? Login now.</p>
                            </div>
                            """)

                            with gr.Row():
                                with gr.Column():
                                    gr.Markdown("""
                                    ### 🚀 Key Features

                                    **👁️ AI Vision Scanning**
                                    • Snap it, scan it, flip it
                                    • 92%+ accuracy with YOLOv8 + TrOCR
                                    • Instant card identification

                                    **💰 Real-Time Price Tracking**
                                    • Live eBay price monitoring
                                    • Historical price trends
                                    • Buy/sell opportunity alerts
                                    """)
                                with gr.Column():
                                    gr.Markdown("""
                                    **🧠 Sentiment Analysis**
                                    • Reddit sentiment tracking
                                    • Flip Score predictions
                                    • Market movement insights

                                    **📊 Portfolio Management**
                                    • Track your card collection
                                    • ROI calculations
                                    • Data export capabilities
                                    """)

                            with gr.Row():
                                learn_more_btn = gr.Button("📖 Learn More", variant="secondary", size="lg")

                            gr.Markdown("---")
                            gr.Markdown("**Built with ❤️ using Gradio, FastAPI, Auth0, and Supabase**")
                            gr.Markdown("*MIT License • [GitHub](https://github.com/b0onzy/dimedrop) • [Contact](mailto:contact@dimedrop.app)*")

                    # Scan Card Tab
                    with gr.Tab("📷 Scan Card", id="scan"):
                        gr.Markdown("## AI Vision Scanning")
                        gr.Markdown("*Snap it, scan it, flip it.*")

                        with gr.Row():
                            image_input = gr.Image(
                                label="Upload Card Image",
                                type="pil",
                                height=300
                            )
                            with gr.Column():
                                scan_button = gr.Button("🔍 Scan Card", variant="primary", size="lg")
                                scan_result = gr.Textbox(
                                    label="Scan Results",
                                    lines=4,
                                    interactive=False
                                )
                                add_to_portfolio_btn = gr.Button("➕ Add to Portfolio", variant="secondary")

                        scan_button.click(
                            self.scan_card_interface,
                            inputs=image_input,
                            outputs=scan_result
                        )

                    # Price Tracking Tab
                    with gr.Tab("💰 Price Tracking", id="price"):
                        gr.Markdown("## Real-Time Price Tracking")
                        gr.Markdown("*Track prices like a pro.*")

                        card_name_input = gr.Textbox(
                            label="Card Name",
                            placeholder="e.g., Wembanyama Prizm",
                            info="Enter the exact card name for best results"
                        )
                        price_button = gr.Button("📊 Get Price Data", variant="primary")
                        price_result = gr.JSON(label="Price Information")

                        price_button.click(
                            self.get_price_interface,
                            inputs=card_name_input,
                            outputs=price_result
                        )

                    # Sentiment Analysis Tab
                    with gr.Tab("🧠 Sentiment Analysis", id="sentiment"):
                        gr.Markdown("## Sentiment Analysis")
                        gr.Markdown("*Read the room, flip the market.*")

                        text_input = gr.Textbox(
                            label="Text to Analyze",
                            placeholder="Enter Reddit post text or market discussion...",
                            lines=4
                        )
                        sentiment_button = gr.Button("🔮 Analyze Sentiment", variant="primary")
                        sentiment_result = gr.JSON(label="Flip Score & Sentiment Breakdown")

                        sentiment_button.click(
                            self.analyze_sentiment_interface,
                            inputs=text_input,
                            outputs=sentiment_result
                        )

                    # Portfolio Management Tab
                    with gr.Tab("📊 Portfolio Management", id="portfolio"):
                        gr.Markdown("## Portfolio Management")
                        gr.Markdown("*Build your card dynasty.*")

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
                            self.update_portfolio_interface,
                            inputs=[action_dropdown, portfolio_card_input, quantity_input],
                            outputs=portfolio_result
                        ).then(
                            self.get_portfolio_interface,
                            outputs=portfolio_display
                        )

                        export_button.click(
                            lambda p: json.dumps({"portfolio": p, "export_date": datetime.now().isoformat()}, indent=2),
                            inputs=portfolio_display,
                            outputs=export_output
                        )

                        # Load portfolio on tab change
                        tabs.select(
                            lambda: gr.Tabs(selected="portfolio"),
                            outputs=tabs
                        ).then(
                            self.get_portfolio_interface,
                            outputs=portfolio_display
                        )

            # Event handlers
            def handle_login():
                """Handle login button click."""
                login_url = self.auth.get_login_url()
                gr.Info("Redirecting to Auth0 login...")
                # In a real app, this would open the URL
                return f"Login URL: {login_url}", gr.update(visible=True)

            def handle_logout():
                """Handle logout."""
                success, message = self.logout_user()
                gr.Info(message)
                return "Not logged in", gr.update(visible=False)

            login_btn.click(
                handle_login,
                outputs=[auth_status, logout_btn]
            )

            logout_btn.click(
                handle_logout,
                outputs=[auth_status, logout_btn]
            )

            # Tab navigation with sidebar buttons
            home_btn.click(lambda: gr.Tabs(selected="home"), outputs=tabs)
            scan_btn.click(lambda: gr.Tabs(selected="scan"), outputs=tabs)
            price_btn.click(lambda: gr.Tabs(selected="price"), outputs=tabs)
            sentiment_btn.click(lambda: gr.Tabs(selected="sentiment"), outputs=tabs)
            portfolio_btn.click(lambda: gr.Tabs(selected="portfolio"), outputs=tabs)

        return app
