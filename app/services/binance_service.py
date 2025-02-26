from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from .redis_service import redis_service
import logging
from typing import Dict, Union, Tuple
import json

logger = logging.getLogger(__name__)

class BinanceService:
    """
    Service for interacting with the Binance API with Redis caching.
    """

    def __init__(self):
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.client = Client(api_key, api_secret)
        self.cache_ttl = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
        self._valid_symbols = set()
        self._init_valid_symbols()
        self._init_cache_metrics()

    def _init_valid_symbols(self):
        """Initialize set of valid trading pairs"""
        try:
            info = self.client.get_exchange_info()
            self._valid_symbols = {s['symbol'] for s in info['symbols'] if s['status'] == 'TRADING'}
        except Exception as e:
            logger.error(f"Failed to initialize symbol list: {str(e)}")
            self._valid_symbols = set()

    def _init_cache_metrics(self):
        """Initialize cache metrics in Redis"""
        try:
            metrics = {
                "cache_hits": 0,
                "cache_misses": 0,
                "last_cache_time": None,
                "frequent_symbols": {}
            }
            redis_service.set_cached_data("stats", metrics)
        except Exception as e:
            logger.error(f"Failed to initialize cache metrics: {str(e)}")

    async def _update_cache_metrics(self, symbol: str, is_hit: bool):
        """Update cache metrics"""
        try:
            stats = await redis_service.get_cached_data("stats") or {
                "cache_hits": 0,
                "cache_misses": 0,
                "frequent_symbols": {}
            }
            
            if is_hit:
                stats["cache_hits"] = stats.get("cache_hits", 0) + 1
            else:
                stats["cache_misses"] = stats.get("cache_misses", 0) + 1

            # Track frequently accessed symbols
            symbols = stats.get("frequent_symbols", {})
            symbols[symbol] = symbols.get(symbol, 0) + 1
            stats["frequent_symbols"] = symbols

            await redis_service.set_cached_data("stats", stats)
        except Exception as e:
            logger.error(f"Failed to update cache metrics: {str(e)}")

    def is_valid_symbol(self, symbol: str) -> bool:
        """Check if a trading pair symbol is valid"""
        if not self._valid_symbols:
            self._init_valid_symbols()
        return symbol.upper() in self._valid_symbols

    def is_active(self) -> bool:
        """
        Check if the Binance API is accessible and the authentication is valid.
        Returns:
            bool: True if authentication succeeds, otherwise False.
        """
        try:
            # The ping method will raise an exception if authentication fails.
            self.client.ping()
            return True
        except BinanceAPIException as e:
            return False
        except Exception as e:
            logger.error(f"Binance connection check failed: {str(e)}")
            return False

    async def get_symbol_price(self, symbol: str) -> Tuple[float, str]:
        """
        Fetch current price for a given trading symbol, with Redis caching.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')
        
        Returns:
            Tuple[float, str]: (price, source) where source is either 'cache' or 'binance'
        """
        symbol = symbol.upper()
        
        if not self.is_valid_symbol(symbol):
            logger.error(f"Invalid trading pair symbol: {symbol}")
            raise ValueError(f"Invalid trading pair symbol: {symbol}. Please use a valid symbol like 'BTCUSDT' or 'ETHBTC'")

        cache_key = f"price:{symbol}"

        # Try to get from cache first
        cached_price = await redis_service.get_cached_data(cache_key)
        if cached_price is not None:
            logger.info(f"Cache hit for {symbol}")
            await self._update_cache_metrics(symbol, True)
            return float(cached_price), "cache"

        # If not in cache, fetch from Binance
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])
            
            # Cache the new price
            await redis_service.set_cached_data(cache_key, price, self.cache_ttl)
            logger.info(f"Cache miss for {symbol}, fetched from Binance")
            await self._update_cache_metrics(symbol, False)
            
            return price, "binance"
        except BinanceAPIException as e:
            logger.error(f"Failed to get price for {symbol}: {str(e)}")
            raise ValueError(f"Failed to get price for {symbol}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {symbol}: {str(e)}")
            raise ValueError(f"Unexpected error fetching price for {symbol}: {str(e)}")

    async def clear_price_cache(self, symbol: str = None) -> bool:
        """
        Clear price cache for a specific symbol or all symbols.
        
        Args:
            symbol (str, optional): Trading pair symbol. If None, clears all price caches.
        """
        pattern = f"price:{symbol.upper()}" if symbol else "price:*"
        return await redis_service.clear_cache(pattern)

# Create a singleton instance
binance_service = BinanceService()
