"""
Cache service implementation.
"""


class CacheService:
    """Service for caching operations."""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    def get(self, key: str):
        """Get value from cache."""
        return self.redis_client.get(key)
    
    def set(self, key: str, value, ttl: int = 3600):
        """Set value in cache with TTL."""
        self.redis_client.setex(key, ttl, value)
    
    def delete(self, key: str):
        """Delete value from cache."""
        self.redis_client.delete(key)
    
    def clear(self):
        """Clear all cache."""
        self.redis_client.flushdb()
