import json
import time
import unittest
from unittest.mock import MagicMock, patch
from redis.exceptions import RedisError
from canonicalwebteam.stores_web_redis.utility import RedisCache


from canonicalwebteam.stores_web_redis.utility import SafeJSONEncoder


class TestSafeJSONEncoder(unittest.TestCase):
    def test_bytes_utf8_decodable(self):
        data = {"b": b"helloworld"}
        self.assertEqual(
            json.dumps(data, cls=SafeJSONEncoder), '{"b": "helloworld"}'
        )

    def test_bytearray_utf8_decodable(self):
        data = {"b": bytearray(b"helloworld")}
        self.assertEqual(
            json.dumps(data, cls=SafeJSONEncoder), '{"b": "helloworld"}'
        )

    def test_bytes_non_utf8(self):
        bad = b"\xff\xfe"
        self.assertEqual(
            json.dumps({"b": bad}, cls=SafeJSONEncoder),
            '{"b": "non-decodable-bytes (2 bytes)"}',
        )

    def test_set_sortable_returns_sorted_list(self):
        data = {"set": {3, 1, 2}}
        loaded = json.loads(json.dumps(data, cls=SafeJSONEncoder))
        self.assertEqual(loaded["set"], [1, 2, 3])

    def test_set_not_sortable_falls_back_to_list(self):
        data = {"set": {1, "a"}}
        loaded = json.loads(json.dumps(data, cls=SafeJSONEncoder))
        self.assertEqual(set(loaded["set"]), {1, "a"})
        self.assertIsInstance(loaded["set"], list)

    def test_tuple_converted_to_list(self):
        data = {"t": (1, 2, 3)}
        loaded = json.loads(json.dumps(data, cls=SafeJSONEncoder))
        self.assertEqual(loaded["t"], [1, 2, 3])
        self.assertIsInstance(loaded["t"], list)

    def test_super_default_raises_typeerror_for_unknown_obj(self):
        class Foo:
            pass

        with self.assertRaises(TypeError):
            json.dumps({"x": Foo()}, cls=SafeJSONEncoder)


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

    def test_build_key_no_parts(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._build_key("abc"), "my-store:abc")

    def test_build_key_multiple_parts(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(
            cache._build_key(("base", {"arch": "x86", "test": "test"})),
            "my-store:base:arch-x86:test-test",
        )

    def test_build_key_falsy_parts(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(
            cache._build_key(
                ("base", {"arch": "", "test": None, "lib": False})
            ),
            "my-store:base",
        )

    def test_serialize_str(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._serialize("abc"), "abc")

    def test_serialize_json(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._serialize({"a": 1}), json.dumps({"a": 1}))

    def test_serialize_set(self):
        cache = RedisCache(namespace="my-store", maxsize=1)
        self.assertEqual(cache._serialize({1, 2}), json.dumps([1, 2]))

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
        value = cache.get(("key", {"arch": "x86"}), expected_type=dict)
        self.assertEqual(value, {"x": 1})

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_get_from_fallback(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.fallback["my-store:key:arch-x86"] = json.dumps(
            {"fallback": True}
        )
        result = cache.get(("key", {"arch": "x86"}), expected_type=dict)
        self.assertEqual((result), {"fallback": True})

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_set_redis_success(self, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.set(("key", {"arch": "x86"}), {"value": 123})
        mock_client.setex.assert_called_once()

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_set_fallback_on_failure(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.set(("key", {"arch": "x86"}), {"fallback": True})
        self.assertEqual(
            json.loads(cache.fallback["my-store:key:arch-x86"]),
            {"fallback": True},
        )

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_delete_from_redis(self, mock_redis):
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.delete(("key", {"arch": "x86"}))
        mock_client.delete.assert_called_once()

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_delete_from_fallback(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1)
        cache.fallback["my-store:key:arch-x86"] = "to-delete"
        cache.delete(("key", {"arch": "x86"}))
        self.assertNotIn(("my-store:key:arch-x86"), cache.fallback)

    @patch("canonicalwebteam.stores_web_redis.utility.redis.Redis")
    def test_ttl_cache_expiry(self, mock_redis):
        instance = mock_redis.return_value
        instance.ping.side_effect = RedisError("Down")

        cache = RedisCache(namespace="my-store", maxsize=1, ttl=1)
        cache.set(("key", {"arch": "x86"}), "value")
        self.assertEqual(cache.get(("key", {"arch": "x86"})), "value")
        time.sleep(1.5)
        self.assertIsNone(cache.get(("key", {"arch": "x86"})))


if __name__ == "__main__":
    unittest.main()
