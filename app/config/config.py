import os
from services.redis_service import redis_service
from services.binance_service import binance_service

# Cache TTL configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
