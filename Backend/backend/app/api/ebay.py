from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import os
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["ebay"])

# Global rate limit tracking (in production, use Redis or database)
call_count = 0
last_reset = time.time()

class ListingQuery(BaseModel):
    card_name: str
    limit: int = 20

    @field_validator('limit')
    @classmethod
    def limit_range(cls, v):
        if v > 100:
            raise ValueError('Limit cannot exceed 100')
        return v

def check_rate_limit():
    global call_count, last_reset
    if time.time() - last_reset > 86400:  # Reset daily
        call_count = 0
        last_reset = time.time()
    if call_count >= 5000:
        raise HTTPException(status_code=429, detail="Daily rate limit reached")
    call_count += 1
    logger.info(f"Call count: {call_count}")

@router.get("/listings")
async def get_ebay_listings(query: ListingQuery):
    logger.info(f"Received request for {query.card_name}")
    try:
        check_rate_limit()

        appid = os.getenv("EBAY_APP_ID")
        if not appid:
            logger.warning("eBay APP_ID not configured, using mock listings")
            # Mock listings
            listings = [
                {
                    'itemId': '123456789',
                    'title': f'{query.card_name} - Mock Listing 1',
                    'currentPrice': 150.0,
                    'bidCount': 5,
                    'endTime': (datetime.now() + timedelta(days=1)).isoformat(),
                    'imageUrl': 'https://via.placeholder.com/300x400?text=Card+Image',
                    'viewItemUrl': 'https://www.ebay.com/itm/123456789',
                    'condition': 'Used',
                    'sellerFeedbackScore': 100,
                },
                {
                    'itemId': '987654321',
                    'title': f'{query.card_name} - Mock Listing 2',
                    'currentPrice': 200.0,
                    'bidCount': 3,
                    'endTime': (datetime.now() + timedelta(days=2)).isoformat(),
                    'imageUrl': 'https://via.placeholder.com/300x400?text=Card+Image',
                    'viewItemUrl': 'https://www.ebay.com/itm/987654321',
                    'condition': 'Used',
                    'sellerFeedbackScore': 95,
                },
            ]
            return {"listings": listings[:query.limit]}

        from ebaysdk.finding import Connection as Finding
        api = Finding(appid=appid, config_file=None)
        response = api.execute('findItemsAdvanced', {
            'keywords': f'{query.card_name} basketball card -graded -slab -psa -beckett',
            'categoryId': '183454',
            'itemFilter': [
                {'name': 'ListingType', 'value': 'Auction'},
                {'name': 'Condition', 'value': 'Used'},
                {'name': 'MinPrice', 'value': '50.00'},
                {'name': 'MaxPrice', 'value': '5000.00'},
            ],
            'sortOrder': 'EndTimeSoonest',
            'paginationInput': {'entriesPerPage': query.limit}
        })
        items = response.reply.get('searchResult', {}).get('item', [])
        if not items:
            logger.warning(f"No listings found for {query.card_name}")
            raise HTTPException(status_code=404, detail="No listings found")
        listings = [{
            'itemId': item['itemId'],
            'title': item['title'],
            'currentPrice': float(item['sellingStatus']['currentPrice']['value']),
            'bidCount': int(item['sellingStatus'].get('bidCount', 0)),
            'endTime': item['listingInfo']['endTime'],
            'imageUrl': item.get('galleryURL'),
            'viewItemUrl': item['viewItemURL'],
            'condition': item['condition'].get('conditionDisplayName', 'Unknown'),
            'sellerFeedbackScore': int(item['sellerInfo'].get('feedbackScore', 0)),
        } for item in items]
        logger.info(f"Successfully fetched {len(listings)} listings")
        return {"listings": listings}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "exceeded the number of times" in error_msg:
            logger.error("eBay rate limit exceeded")
            raise HTTPException(status_code=429, detail="eBay API rate limit exceeded")
        logger.error(f"API error: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {error_msg}")