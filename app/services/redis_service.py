import redis
import logging
import json
import os
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self._init_redis_client()

    def _init_redis_client(self):
        """Initialize Redis client with retry configuration"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=0,
                decode_responses=True,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            if not self.is_connected():
                logger.error("Failed to connect to Redis during initialization")
        except Exception as e:
            logger.error(f"Error initializing Redis client: {str(e)}")
            self.redis_client = None

    def is_connected(self) -> bool:
        """Check Redis connection status"""
        try:
            if not self.redis_client:
                self._init_redis_client()
                if not self.redis_client:
                    return False
            return self.redis_client.ping()
        except redis.ConnectionError as e:
            logger.error(f"Cannot connect to Redis at {self.redis_host}:{self.redis_port}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking Redis connection: {str(e)}")
            return False

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Retrieve data from cache with connection retry"""
        if not self.is_connected():
            logger.warning("Redis not connected, attempting to reconnect...")
            self._init_redis_client()
            
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON data from Redis: {str(e)}")
            self.redis_client.delete(key)  # Remove invalid data
            return None
        except Exception as e:
            logger.error(f"Error retrieving data from Redis: {str(e)}")
            return None

    async def set_cached_data(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Store data in cache with connection retry"""
        if not self.is_connected():
            logger.warning("Redis not connected, attempting to reconnect...")
            self._init_redis_client()
            
        try:
            serialized_value = json.dumps(value)
            success = self.redis_client.setex(key, ttl, serialized_value)
            if success:
                await self._update_last_write(key)
            return bool(success)
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error storing data in Redis: {str(e)}")
            return False

    async def _update_last_write(self, key: str):
        """Track last write time for cache entries"""
        try:
            metadata_key = f"metadata:{key}"
            metadata = {
                "last_write": datetime.utcnow().isoformat(),
                "key": key
            }
            self.redis_client.setex(metadata_key, 86400, json.dumps(metadata))  # 24h TTL for metadata
        except Exception as e:
            logger.error(f"Error updating cache metadata: {str(e)}")

    async def delete_cached_data(self, key: str) -> bool:
        """Remove data from cache with metadata cleanup"""
        if not self.is_connected():
            return False
            
        try:
            deleted = bool(self.redis_client.delete(key))
            if deleted:
                self.redis_client.delete(f"metadata:{key}")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting data from Redis: {str(e)}")
            return False

    async def clear_cache(self, pattern: str = "*") -> bool:
        """Clear all cached data matching pattern with metadata cleanup"""
        if not self.is_connected():
            return False
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                # Delete both data and metadata
                metadata_keys = [f"metadata:{key}" for key in keys]
                all_keys = keys + metadata_keys
                return bool(self.redis_client.delete(*all_keys))
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {str(e)}")
            return False

# Create a singleton instance
redis_service = RedisService()