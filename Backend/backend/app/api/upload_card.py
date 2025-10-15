from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
import os
import json
from typing import Optional
from supabase import create_client, Client
from ebaysdk.finding import Connection as Finding
from app.services.auth import get_current_user
from app.core.database import PortfolioOperations
from app.core.models import Portfolio

router = APIRouter()

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for server-side operations

    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")

    return create_client(url, key)

def get_ebay_price_estimate(player: str, year: int, card_set: str) -> Optional[float]:
    """Get price estimate from eBay API"""
    try:
        app_id = os.getenv('EBAY_APP_ID')
        if not app_id:
            return None

        api = Finding(appid=app_id, config_file=None)

        # Search for the card
        search_query = f"{player} {year} {card_set} basketball card"
        response = api.execute('findItemsByKeywords', {
            'keywords': search_query,
            'categoryId': '213',  # Sports Memorabilia > Cards
            'itemFilter': [
                {'name': 'Condition', 'value': 'Used'},
                {'name': 'Currency', 'value': 'USD'}
            ],
            'paginationInput': {'entriesPerPage': '10'}
        })

        # Handle response properly - eBay SDK returns XML that can be converted to dict
        try:
            response_data = response.dict() if hasattr(response, 'dict') else {}
        except:
            response_data = {}

        if not isinstance(response_data, dict):
            return None

        search_result = response_data.get('searchResult', {})
        items = search_result.get('item', []) if isinstance(search_result, dict) else []

        if not items or not isinstance(items, list):
            return None

        # Calculate average price from top 5 results
        prices = []
        for item in items[:5]:
            try:
                if isinstance(item, dict):
                    current_price = float(item.get('sellingStatus', {}).get('currentPrice', {}).get('value', 0))
                    if current_price > 0:
                        prices.append(current_price)
            except (ValueError, TypeError, KeyError):
                continue

        return sum(prices) / len(prices) if prices else None

    except Exception as e:
        print(f"eBay API error: {e}")
        return None

@router.post("/upload-card")
async def upload_card(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a card image, extract metadata, and add to portfolio
    """
    try:
        # Parse metadata
        card_metadata = json.loads(metadata)
        player = card_metadata.get('player', '').strip()
        year = card_metadata.get('year', 2023)
        card_set = card_metadata.get('set', '').strip()

        if not player:
            raise HTTPException(status_code=400, detail="Player name is required")

        # Get user ID from JWT
        user_id = current_user.get('sub')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")

        # Initialize Supabase client
        supabase = get_supabase_client()

        # Create user-specific bucket path
        bucket_name = "card-images"
        file_path = f"{user_id}/{player.replace(' ', '_')}_{year}_{card_set.replace(' ', '_')}.jpg"

        # Read file content
        file_content = await file.read()

        # Upload to Supabase Storage
        try:
            supabase.storage.from_(bucket_name).upload(
                file_path,
                file_content,
                file_options={
                    "content-type": file.content_type or "image/jpeg",
                    "cache-control": "3600"
                }
            )

            # Get public URL
            image_url = supabase.storage.from_(bucket_name).get_public_url(file_path)

        except Exception as e:
            print(f"Supabase upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload image")

        # Get price estimate from eBay
        estimated_price = get_ebay_price_estimate(player, year, card_set)

        # Add to portfolio database using the correct method
        try:
            portfolio_entry = PortfolioOperations.add_card(
                card_name=f"{player} {year} {card_set}",
                purchase_price=estimated_price,  # Use estimated price as initial buy price
                quantity=1,
                condition="Raw",
                user_id=user_id,
                notes=f"Scanned card - Image: {image_url}"
            )

            if not portfolio_entry:
                raise HTTPException(status_code=500, detail="Failed to save card to portfolio")

        except Exception as e:
            print(f"Database error: {e}")
            # Try to clean up uploaded file if database insert fails
            try:
                supabase.storage.from_(bucket_name).remove([file_path])
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to save card to portfolio")

        return {
            "success": True,
            "cardId": portfolio_entry.get('id') if portfolio_entry else None,
            "imageUrl": image_url,
            "estimatedPrice": estimated_price,
            "message": f"Successfully added {player} {year} {card_set} to portfolio"
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata format")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")