"""
Home component for DimeDrop Gradio app.
Professional dashboard with hero section and feature cards.
"""

import gradio as gr


class HomeComponent:
    """Home page component with modern dashboard design."""

    def __init__(self):
        pass

    def render(self):
        """Render the modern home dashboard."""

        # Hero Section
        gr.HTML("""
        <div class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">Welcome to DimeDrop</h1>
                <p class="hero-subtitle">The ultimate platform for basketball card flipping and investment</p>

                <div class="hero-stats">
                    <div class="hero-stat">
                        <span class="hero-stat-value">$2.4M+</span>
                        <span class="hero-stat-label">Cards Tracked</span>
                    </div>
                    <div class="hero-stat">
                        <span class="hero-stat-value">15K+</span>
                        <span class="hero-stat-label">Active Users</span>
                    </div>
                    <div class="hero-stat">
                        <span class="hero-stat-value">92%</span>
                        <span class="hero-stat-label">Accuracy Rate</span>
                    </div>
                </div>
            </div>
        </div>
        """)

        # Feature Grid
        gr.HTML('<h2 style="text-align: center; margin: 40px 0 24px 0; color: #FFFFFF; font-size: 28px; font-weight: 600;">Powerful Tools for Card Investors</h2>')

        with gr.Row(elem_classes="feature-grid"):
            # AI Vision Scanning
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-icon">📷</div>
                <h3 class="feature-title">AI Vision Scanning</h3>
                <p class="feature-description">Snap a photo of any basketball card and instantly identify it with 92%+ accuracy using advanced YOLOv8 and TrOCR technology.</p>
            </div>
            """)

            # Real-Time Price Tracking
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <h3 class="feature-title">Real-Time Price Tracking</h3>
                <p class="feature-description">Monitor live eBay prices, track historical trends, and get instant alerts when cards hit your target prices.</p>
            </div>
            """)

            # Sentiment Analysis
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3 class="feature-title">Sentiment Analysis</h3>
                <p class="feature-description">AI-powered analysis of Reddit discussions to predict card value movements and market sentiment.</p>
            </div>
            """)

        with gr.Row(elem_classes="feature-grid"):
            # Portfolio Management
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">Portfolio Management</h3>
                <p class="feature-description">Track your investments, calculate ROI, and manage your entire basketball card collection in one place.</p>
            </div>
            """)

            # Market Intelligence
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3 class="feature-title">Market Intelligence</h3>
                <p class="feature-description">Get insights on trending cards, upcoming releases, and market opportunities powered by real-time data.</p>
            </div>
            """)

            # Secure & Private
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3 class="feature-title">Secure & Private</h3>
                <p class="feature-description">Your data is protected with enterprise-grade security, Auth0 authentication, and Supabase encryption.</p>
            </div>
            """)

        # Quick Actions Section
        gr.HTML('<h2 style="text-align: center; margin: 40px 0 24px 0; color: #FFFFFF; font-size: 24px; font-weight: 600;">Get Started Today</h2>')

        with gr.Row():
            with gr.Column():
                gr.Button("📷 Scan Your First Card", variant="primary", size="lg")
                gr.Markdown("*Upload a card image to get started*")

            with gr.Column():
                gr.Button("💰 Browse Price Tracker", variant="secondary", size="lg")
                gr.Markdown("*Explore current market prices*")

            with gr.Column():
                gr.Button("📊 View Portfolio", variant="secondary", size="lg")
                gr.Markdown("*Manage your collection*")

        return gr.Blocks()
