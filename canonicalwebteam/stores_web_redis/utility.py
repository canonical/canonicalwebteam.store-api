import os
from cachetools import TTLCache
import redis
import json
import logging
from typing import Optional, Any, Union

logger = logging.getLogger(__name__)

host = os.getenv("REDIS_DB_HOSTNAME", "localhost")
port = os.getenv("REDIS_DB_PORT", "6379")
password = os.getenv("REDIS_DB_PASSWORD", None)


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            try:
                return bytes(obj).decode("utf-8")
            except UnicodeDecodeError:
                return f"non-decodable-bytes ({len(obj)} bytes)"

        if isinstance(obj, set):
            try:
                return sorted(obj)
            except Exception:
                return list(obj)
        if isinstance(obj, tuple):
            return list(obj)
        return super().default(obj)


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

    def _build_key(
        self, key: Union[str, tuple[str, Optional[dict[str, Any]]]]
    ) -> str:
        base_key, parts = key if isinstance(key, tuple) else (key, {})
        key_parts = ":".join(f"{k}-{v}" for k, v in parts.items() if v)
        full_key = (
            f"{self.namespace}:{base_key}:{key_parts}"
            if key_parts
            else f"{self.namespace}:{base_key}"
        )
        return full_key

    def _serialize(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, cls=SafeJSONEncoder)
        except (TypeError, ValueError) as e:
            logger.error("Serialization error: %s", e)
            raise

    def _deserialize(
        self, value: Optional[str], expected_type: type = str
    ) -> Any:
        if value is None:
            return None
        if expected_type is str:
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError) as e:
            logger.error("Deserialization error: %s", e)
            raise

    def get(
        self,
        key: Union[str, tuple[str, Optional[dict[str, Any]]]],
        expected_type: type = str,
    ) -> Any:
        full_key = self._build_key(key)
        if self.redis_available:
            try:
                return self._deserialize(
                    self.client.get(full_key), expected_type
                )
            except redis.RedisError as e:
                logger.error("Redis get error: %s", e)
        else:
            try:
                return self._deserialize(
                    self.fallback[full_key], expected_type
                )
            except KeyError:
                return None
            except Exception as e:
                logger.error("Fallback cache get error: %s", e)

    def set(
        self,
        key: Union[str, tuple[str, Optional[dict[str, Any]]]],
        value: Any,
        ttl=300,
    ):
        full_key = self._build_key(key)
        serialized = self._serialize(value)
        if self.redis_available:
            try:
                self.client.setex(full_key, ttl, serialized)
                return
            except redis.RedisError as e:
                logger.error("Redis set error: %s", e)
        else:
            try:
                self.fallback[full_key] = serialized
            except Exception as e:
                logger.error("Fallback cache set error: %s", e)

    def delete(self, key: Union[str, tuple[str, Optional[dict[str, Any]]]]):
        full_key = self._build_key(key)
        if self.redis_available:
            try:
                self.client.delete(full_key)
            except redis.RedisError as e:
                logger.error("Redis delete error: %s", e)
        else:
            self.fallback.pop(full_key, None)
