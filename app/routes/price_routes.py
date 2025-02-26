from fastapi import APIRouter, HTTPException
from app.config.config import binance_service
import logging
from typing import Dict, Union

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/price/{symbol}",
    response_model=Dict[str, Union[float, str]],
    responses={
        200: {
            "description": "Successfully retrieved price",
            "content": {
                "application/json": {
                    "examples": {
                        "cached": {"value": {"price": 45000.50, "source": "cache"}},
                        "live": {"value": {"price": 45000.50, "source": "binance"}},
                    }
                }
            },
        },
        400: {
            "description": "Invalid symbol or request",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid trading pair symbol: INVALID. Please use a valid symbol like 'BTCUSDT' or 'ETHBTC'"}
                }
            }
        },
        500: {"description": "Internal server error"},
    },
)
async def get_price(symbol: str):
    """
    Get current price for a cryptocurrency trading pair.
    Uses Redis caching with fallback to Binance API.
    """
    try:
        if not binance_service.is_active():
            raise HTTPException(
                status_code=500,
                detail="Binance service is not available"
            )
            
        price, source = await binance_service.get_symbol_price(symbol)
        return {"price": price, "source": source}
        
    except ValueError as e:
        logger.error(f"Error fetching price for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
