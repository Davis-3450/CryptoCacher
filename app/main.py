from fastapi import FastAPI, HTTPException
from app.routes import metrics_routes
from app.routes import price_routes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CryptoCacher",
    description="""
    High-performance cryptocurrency price caching service.
    
    Features:
    - Fast price lookups via Redis cache
    - Automatic fallback to Binance API
    - Performance metrics and monitoring
    - Configurable cache TTL
    
    For detailed API documentation, visit /docs
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(price_routes.router, tags=["prices"])
app.include_router(metrics_routes.router, prefix="/metrics", tags=["metrics"])

def is_active_binance():
    try:
        from app.config.config import binance_service
        return binance_service.is_active()
    except Exception as e:
        logger.error(f"Error checking Binance status: {str(e)}")
        return False

@app.get("/", tags=["health"])
async def health_check():
    return {"status": "healthy",
            "binance": is_active_binance()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
