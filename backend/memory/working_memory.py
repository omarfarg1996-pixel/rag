"""
Working Memory Layer - Redis-based short-term memory
Handles conversation context, temporary variables, and session state
"""
import redis.asyncio as redis
from typing import Any, Dict, Optional, List
from datetime import timedelta
import json
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class WorkingMemory:
    """Redis-backed working memory for active session data"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.default_ttl = settings.REDIS_DEFAULT_TTL
    
    async def connect(self) -> None:
        """Initialize Redis connection pool"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS
            )
            await self.redis.ping()
            logger.info("WorkingMemory connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("WorkingMemory disconnected from Redis")
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set a value in working memory
        
        Args:
            key: Memory key
            value: Value to store (will be JSON serialized)
            ttl: Time-to-live in seconds (default from settings)
            nx: Only set if key doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            
            if nx:
                result = await self.redis.set(key, serialized, ex=ttl, nx=True)
                return bool(result)
            else:
                await self.redis.set(key, serialized, ex=ttl)
                return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from working memory
        
        Args:
            key: Memory key
            
        Returns:
            Deserialized value or None if not found
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting keys: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key existence: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on a key"""
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Error setting expiration: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for a key (-1 if no TTL, -2 if key doesn't exist)"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL: {e}")
            return -2
    
    async def hset(self, name: str, key: str, value: Any) -> int:
        """Set a field in a hash"""
        try:
            serialized = json.dumps(value)
            return await self.redis.hset(name, key, serialized)
        except Exception as e:
            logger.error(f"Error hset: {e}")
            return 0
    
    async def hget(self, name: str, key: str) -> Optional[Any]:
        """Get a field from a hash"""
        try:
            value = await self.redis.hget(name, key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error hget: {e}")
            return None
    
    async def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all fields from a hash"""
        try:
            data = await self.redis.hgetall(name)
            return {k: json.loads(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error hgetall: {e}")
            return {}
    
    async def incr(self, key: str) -> int:
        """Increment a key's value"""
        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Error incrementing: {e}")
            return 0
    
    async def scan_keys(self, pattern: str, count: int = 100) -> List[str]:
        """Scan for keys matching a pattern"""
        try:
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self.redis.scan(cursor, match=pattern, count=count)
                keys.extend(batch)
                if cursor == 0:
                    break
            return keys
        except Exception as e:
            logger.error(f"Error scanning keys: {e}")
            return []
    
    async def get_memory_info(self) -> Dict[str, Any]:
        """Get Redis memory information"""
        try:
            info = await self.redis.info("memory")
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "maxmemory": info.get("maxmemory", 0),
                "maxmemory_human": info.get("maxmemory_human", "0B"),
                "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio", 0),
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {}
    
    # Session-specific methods
    async def save_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save conversation session"""
        key = f"session:{session_id}"
        return await self.set(key, data, ttl=3600)  # 1 hour default
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation session"""
        key = f"session:{session_id}"
        return await self.get(key)
    
    async def add_to_conversation(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add a message to conversation history"""
        key = f"conversation:{session_id}"
        message = {
            "role": role,
            "content": content,
            "timestamp": __import__("time").time(),
            "metadata": metadata or {}
        }
        
        # Use list for ordered conversation
        await self.redis.rpush(key, json.dumps(message))
        await self.redis.expire(key, self.default_ttl)
        return True
    
    async def get_conversation(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent conversation messages"""
        key = f"conversation:{session_id}"
        try:
            messages = await self.redis.lrange(key, -limit, -1)
            return [json.loads(msg) for msg in messages]
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return []
    
    async def clear_session(self, session_id: str) -> bool:
        """Clear all session data"""
        keys = [
            f"session:{session_id}",
            f"conversation:{session_id}",
            f"context:{session_id}"
        ]
        return await self.delete(*keys) > 0


# Global instance
working_memory = WorkingMemory()


async def get_working_memory() -> WorkingMemory:
    """Get working memory instance"""
    return working_memory
