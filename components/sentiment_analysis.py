"""
Sentiment Analysis component for DimeDrop Gradio app.
Handles sentiment analysis for market discussions.
"""

import gradio as gr


class SentimentAnalyzerComponent:
    """Sentiment analysis component with text input and analysis."""

    def __init__(self, api_manager):
        self.api = api_manager

    def analyze_sentiment(self, text):
        """Analyze sentiment of input text."""
        if not text.strip():
            return {"error": "Please enter text to analyze."}

        # For demo, analyze the text directly
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

    def render(self):
        """Render the sentiment analysis component content."""
        gr.Markdown("## Sentiment Analysis")
        gr.Markdown("*Feel the hype.*")

        text_input = gr.Textbox(
            label="Text to Analyze",
            placeholder="Enter Reddit post text or market discussion...",
            lines=4
        )
        sentiment_button = gr.Button("🔮 Analyze Sentiment", variant="primary")
        sentiment_result = gr.JSON(label="Flip Score & Sentiment Breakdown")

        sentiment_button.click(
            self.analyze_sentiment,
            inputs=[text_input],
            outputs=sentiment_result
        )
