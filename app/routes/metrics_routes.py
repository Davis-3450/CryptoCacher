from fastapi import APIRouter, HTTPException
from app.services.redis_service import redis_service
import logging
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=Dict[str, Any])
async def get_metrics():
    """
    Return detailed cache metrics and statistics.
    Includes cache hits/misses, most frequently accessed symbols,
    and cache health status.
    """
    try:
        # Check Redis connection
        redis_status = redis_service.is_connected()
        
        # Get cache statistics
        stats = await redis_service.get_cached_data("stats")
        if stats is None:
            stats = {"cache_hits": 0, "cache_misses": 0, "frequent_symbols": {}}
        
        # Calculate cache hit ratio
        total_requests = stats["cache_hits"] + stats["cache_misses"]
        hit_ratio = (stats["cache_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # Get top accessed symbols
        frequent_symbols = stats.get("frequent_symbols", {})
        top_symbols = dict(sorted(frequent_symbols.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:5])

        return {
            "redis_connected": redis_status,
            "cache_stats": {
                "hits": stats["cache_hits"],
                "misses": stats["cache_misses"],
                "hit_ratio": round(hit_ratio, 2),
                "top_symbols": top_symbols
            },
            "status": "healthy" if redis_status else "degraded"
        }
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/cache/{symbol}")
async def clear_symbol_cache(symbol: str):
    """Clear cache for a specific trading pair"""
    try:
        success = await redis_service.delete_cached_data(f"price:{symbol.upper()}")
        return {"success": success, "message": f"Cache cleared for {symbol}"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/cache")
async def clear_all_cache():
    """Clear all price caches"""
    try:
        success = await redis_service.clear_cache("price:*")
        return {"success": success, "message": "All price caches cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
