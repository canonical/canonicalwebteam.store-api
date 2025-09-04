import json
import time
import unittest
from unittest.mock import MagicMock, patch
from redis.exceptions import RedisError
from cachetools import TTLCache
from canonicalwebteam.stores_web_redis.utility import RedisCache
import canonicalwebteam.stores_web_redis.utility as u




class TestRedisCache(unittest.TestCase):

    def setUp(self):
        self.namespace = "test"
        self.maxsize = 2
        self.ttl = 2

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_redis_available(self, mock_redis):
        mock_redis.return_value.ping.return_value = True
        cache = RedisCache(namespace=self.namespace, maxsize=self.maxsize)
        self.assertTrue(cache.redis_available)
        mock_redis.return_value.ping.assert_called_once()

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_redis_unavailable(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace=self.namespace, maxsize=self.maxsize)
        self.assertFalse(cache.redis_available)

    def test_build_key(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._build_key("abc"), "my-store:abc")

    def test_serialize_str(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._serialize("abc"), "abc")

    def test_serialize_json(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._serialize({"a": 1}), json.dumps({"a": 1}))

    def test_serialize_invalid(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        with self.assertRaises(TypeError):
            cache._serialize({1, 2})

    def test_deserialize_str(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._deserialize("abc", str), "abc")

    def test_deserialize_json(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._deserialize('{"a":1}', dict), {"a": 1})

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_get_from_redis(self, mock_redis):
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = '{"x": 1}'
        mock_redis.return_value = mock_client

        cache = RedisCache(namespace="my-store", maxsize=1)
        value = cache.get("key", expected_type=dict)
        self.assertEqual(value, {"x": 1})

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_get_from_fallback(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.fallback["key"] = {"fallback": True}
        result = cache.get("key", expected_type=dict)
        self.assertEqual(result, {"fallback": True})

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_set_redis_success(self, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.set("key", {"value": 123})
        mock_client.setex.assert_called_once()

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_set_fallback_on_failure(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.set("key", {"fallback": True})
        self.assertEqual(cache.fallback["key"], {"fallback": True})

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_delete_from_redis(self, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.delete("key")
        mock_client.delete.assert_called_once()

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_delete_from_fallback(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.fallback["key"] = "to-delete"
        cache.delete("key")
        self.assertNotIn("key", cache.fallback)

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_ttl_cache_expiry(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1, ttl=1)
        cache.set("key", "value")
        self.assertEqual(cache.get("key"), "value")
        time.sleep(1.5)
        self.assertIsNone(cache.get("key"))


if __name__ == "__main__":
    unittest.main()
