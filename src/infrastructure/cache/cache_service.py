"""
Cache service for distributed caching.
"""
import json
import redis
from typing import Any, Optional, Dict
from datetime import timedelta


class CacheService:
    """Abstract cache service interface."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache."""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError
    
    def clear(self) -> bool:
        """Clear entire cache."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache."""
        raise NotImplementedError


class RedisCacheService(CacheService):
    """Redis-based cache service implementation."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 db: int = 0, password: Optional[str] = None):
        """
        Initialize Redis cache service.
        
        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            print(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis cache with TTL."""
        try:
            # Serialize to JSON if needed
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self.redis_client.setex(
                key,
                timedelta(seconds=ttl),
                value
            )
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear entire Redis database."""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error for key {key}: {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in Redis."""
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error for key {key}: {str(e)}")
            return 0
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """Get multiple values from cache."""
        try:
            values = self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
            return result
        except Exception as e:
            print(f"Cache get_many error: {str(e)}")
            return {}
    
    def set_many(self, mapping: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set multiple values in cache."""
        try:
            # Serialize dict values
            serialized = {}
            for key, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized[key] = json.dumps(value)
                else:
                    serialized[key] = value
            
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            for key, value in serialized.items():
                pipe.setex(key, timedelta(seconds=ttl), value)
            pipe.execute()
            return True
        except Exception as e:
            print(f"Cache set_many error: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete_pattern error: {str(e)}")
            return 0


class InMemoryCacheService(CacheService):
    """In-memory cache service for development and testing."""
    
    def __init__(self):
        """Initialize in-memory cache."""
        self._cache: Dict[str, tuple] = {}  # {key: (value, expiry_time)}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from in-memory cache."""
        import time
        
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if expiry and time.time() > expiry:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in in-memory cache."""
        import time
        
        expiry = time.time() + ttl if ttl else None
        self._cache[key] = (value, expiry)
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from in-memory cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """Clear entire in-memory cache."""
        self._cache.clear()
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory cache."""
        if key not in self._cache:
            return False
        
        value, expiry = self._cache[key]
        if expiry:
            import time
            if time.time() > expiry:
                del self._cache[key]
                return False
        
        return True
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in in-memory cache."""
        if key not in self._cache:
            self._cache[key] = (amount, None)
            return amount
        
        value, expiry = self._cache[key]
        if isinstance(value, int):
            new_value = value + amount
            self._cache[key] = (new_value, expiry)
            return new_value
        
        return 0
