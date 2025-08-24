from typing import Dict, Any, Optional
import time
import logging
import json
from datetime import datetime, timedelta

# Set up logger
logger = logging.getLogger("tradebot.database.cache")

class MarketCache:
    """
    Simple in-memory cache for market data to reduce database queries
    """
    
    def __init__(self, ttl_seconds: int = 60):
        """
        Initialize cache
        
        Args:
            ttl_seconds (int): Time-to-live for cache entries in seconds
        """
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        logger.info(f"Market cache initialized with TTL of {ttl_seconds} seconds")
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
        """
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"Cache set: {key}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[Any]: Cached value or None if not found or expired
        """
        if key not in self.cache:
            logger.debug(f"Cache miss: {key}")
            return None
            
        entry = self.cache[key]
        current_time = time.time()
        
        # Check if entry has expired
        if current_time - entry['timestamp'] > self.ttl_seconds:
            logger.debug(f"Cache expired: {key}")
            del self.cache[key]
            return None
            
        logger.debug(f"Cache hit: {key}")
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: True if key was deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache delete: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache = {}
        logger.info("Cache cleared")
    
    def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached market data for a symbol
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            Optional[Dict[str, Any]]: Cached market data or None
        """
        key = f"market_data:{symbol}"
        return self.get(key)
    
    def set_market_data(self, symbol: str, data: Dict[str, Any]) -> None:
        """
        Cache market data for a symbol
        
        Args:
            symbol (str): Trading pair symbol
            data (Dict[str, Any]): Market data
        """
        key = f"market_data:{symbol}"
        self.set(key, data)
    
    def invalidate_market_data(self, symbol: str) -> None:
        """
        Invalidate cached market data for a symbol
        
        Args:
            symbol (str): Trading pair symbol
        """
        key = f"market_data:{symbol}"
        self.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        current_time = time.time()
        active_entries = 0
        expired_entries = 0
        
        for key, entry in list(self.cache.items()):
            if current_time - entry['timestamp'] <= self.ttl_seconds:
                active_entries += 1
            else:
                expired_entries += 1
                
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'ttl_seconds': self.ttl_seconds
        }

# Create a global instance of the cache
market_cache = MarketCache()