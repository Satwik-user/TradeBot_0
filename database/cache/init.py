"""
Caching implementation for TradeBot application.

This package contains caching mechanisms to improve performance.
"""

__all__ = [
    'market_cache',
]

from database.cache.market_cache import market_cache

# Export the global cache instance
__instance__ = market_cache