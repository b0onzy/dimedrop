"""
Scan Card component for DimeDrop Gradio app.
Handles AI vision scanning of basketball cards.
"""

import gradio as gr
import io
import cv2
import numpy as np
from typing import Optional


class ScanCardComponent:
    """Scan card component with image upload and AI scanning."""

    def __init__(self, api_manager):
        self.api = api_manager

    def preprocess_image(self, image) -> Optional[bytes]:
        """Preprocess image for scanning."""
        if image is None:
            return None
        # Convert PIL to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        # Preprocess with OpenCV
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            # Resize for efficiency
            img = cv2.resize(img, (640, 480))
            # Convert back to bytes
            _, encoded_img = cv2.imencode('.jpg', img)
            return encoded_img.tobytes()
        return img_bytes

    def scan_card(self, image, token):
        """Handle card scanning."""
        if not token:
            return "❌ Please login to use this feature."

        if image is None:
            return "❌ Please upload a card image."

        img_bytes = self.preprocess_image(image)
        if not img_bytes:
            return "❌ Failed to process image."

        result = self.api.scan_card(img_bytes, token)

        if "error" in result:
            return f"⚠️ {result['error']}\nMock Result: LeBron James Rookie Card (92% confidence)"

        return f"✅ Card identified: {result.get('card_name', 'Unknown')}\nConfidence: {result.get('confidence', 0)*100:.1f}%"

    def render(self):
        """Render the scan card component content."""
        gr.Markdown("## AI Vision Scanning")
        gr.Markdown("*Snap it, flip it.*")

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
            self.scan_card,
            inputs=[image_input, gr.State()],  # token will be passed via state
            outputs=scan_result
        )
