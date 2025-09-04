import os
from cachetools import TTLCache
import redis
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

host = os.getenv("REDIS_DB_HOSTNAME", "localhost")
port = os.getenv("REDIS_DB_PORT", "6379")
password = os.getenv("REDIS_DB_PASSWORD", None)


class RedisCache:
    def __init__(self, namespace: str, maxsize: int, ttl: int = 300):
        self.namespace = namespace
        self.fallback = TTLCache(maxsize=maxsize, ttl=ttl)
        try:
            self.client = redis.Redis(
                host=host,
                port=int(port),
                password=password,
                decode_responses=True,
            )
            self.client.ping()
            self.redis_available = True
        except redis.RedisError as e:
            logger.warning("Redis unavailable: %s", e)
            self.redis_available = False

    def _build_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def _serialize(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value)
        except (TypeError, ValueError) as e:
            logger.error("Serialization error: %s", e)
            raise

    def _deserialize(self, value: Optional[str], expected_type: str) -> Any:
        if value is None:
            return None
        if expected_type is str:
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError) as e:
            logger.error("Deserialization error: %s", e)
            raise

    def get(self, key: str, expected_type: str) -> Any:
        if self.redis_available:
            full_key = self._build_key(key)
            try:
                value = self.client.get(full_key)
                return self._deserialize(value, expected_type)
            except redis.RedisError as e:
                logger.error("Redis get error: %s", e)
        value = self.fallback.get(key)
        return value

    def set(self, key: str, value: Any, ttl=300):
        if self.redis_available:
            full_key = self._build_key(key)
            try:
                serialized = self._serialize(value)
                self.client.setex(full_key, ttl, serialized)
                return
            except redis.RedisError as e:
                logger.error("Redis set error: %s", e)
        self.fallback[key] = value

    def delete(self, key: str):
        if self.redis_available:
            full_key = self._build_key(key)
            try:
                self.client.delete(full_key)
            except redis.RedisError as e:
                logger.error("Redis delete error: %s", e)
        else:
            self.fallback.pop(key, None)
