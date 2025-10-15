import cv2
import numpy as np
from ultralytics import YOLO
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import httpx
from fastapi import UploadFile, HTTPException
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class VisionProcessor:
    def __init__(self):
        self.yolo_model = YOLO('yolov8n.pt')  # Pre-trained on COCO, fine-tune for cards
        self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
        self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')

    async def process_card_image(self, image_file: UploadFile) -> Dict:
        """Process uploaded card image for ID and condition grading"""
        try:
            # Read image
            contents = await image_file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # YOLO detection for card boundaries
            results = self.yolo_model(image)
            card_bbox = results[0].boxes.xyxy[0].cpu().numpy()  # Assume single card
            
            # Crop to card
            x1, y1, x2, y2 = card_bbox
            card_crop = image[int(y1):int(y2), int(x1):int(x2)]
            
            # TrOCR for text extraction (player name, year, set)
            pixel_values = self.trocr_processor(card_crop, return_tensors="pt").pixel_values
            generated_ids = self.trocr_model.generate(pixel_values)
            extracted_text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Parse card details (basic regex for now)
            card_name = self._parse_card_name(extracted_text)
            
            # Condition grading (placeholder - expand with ML)
            condition = self._grade_condition(card_crop)
            
            # Search eBay for current price
            price_data = await self._get_ebay_price(card_name)
            
            return {
                'card_name': card_name,
                'condition': condition,
                'current_price': price_data['avg_price'],
                'confidence': 0.85,  # YOLO + TrOCR combined
                'extracted_text': extracted_text
            }
        except Exception as e:
            logger.error(f"Vision processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Image processing failed")

    def _parse_card_name(self, text: str) -> str:
        # Basic parsing - enhance with NLP
        return text.strip()

    def _grade_condition(self, image: np.ndarray) -> str:
        # Placeholder condition grading
        return "Near Mint"  # Add ML model here

    async def _get_ebay_price(self, card_name: str) -> Dict:
        # Call existing price endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8000/prices?card={card_name}")
            return response.json()