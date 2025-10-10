import unittest

from requests import Session
from requests.models import Response, Request
from typing import Dict, cast
from unittest.mock import Mock, MagicMock

from canonicalwebteam.exceptions import (
    StoreApiInternalError,
    StoreApiNotImplementedError,
    StoreApiBadGatewayError,
    StoreApiServiceUnavailableError,
    StoreApiGatewayTimeoutError,
    StoreApiConnectionError,
    StoreApiResponseError,
)
from canonicalwebteam.store_api.base import (
    Base,
    logger as LOGGER,
)


STATUS_MAPPING = {
    500: StoreApiInternalError,
    501: StoreApiNotImplementedError,
    502: StoreApiBadGatewayError,
    503: StoreApiServiceUnavailableError,
    504: StoreApiGatewayTimeoutError,
}

SAMPLE_URL = "http://www.test.com"


def build_response(status_code: int):
    # the request is used by the logging messages
    request = Mock(spec=Request)
    request.url = SAMPLE_URL
    request.headers = {}
    request._cookies = {}
    request.body = ""

    response = Mock(spec=Response)
    response.status_code = status_code
    response.url = request.url
    response.headers = {}
    response.cookies = {}
    response.request = request
    response.json = MagicMock(return_value={})

    if status_code >= 400:
        response.ok = False

    return response


class TestBase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.client = Base(Mock(spec=Session))

    def test_process_response_known_status(self):
        for status, exception in STATUS_MAPPING.items():
            response = build_response(status)
            with self.assertRaises(exception):
                self.client.process_response(response)

    def test_process_response_unknown_status(self):
        response = build_response(599)  # unknown code
        with self.assertRaises(StoreApiConnectionError):
            self.client.process_response(response)

    def test_process_response_not_ok(self):
        class NonSerializableClass:
            pass

        for body, expected_log in [
            ("test", "test"),
            ("test".encode(), "test"),
            # chinese characters that mean "test", encoded with "gbk"
            (b"\xb2\xe2\xca\xd4", "<len 4>"),
            (NonSerializableClass(), "NonSerializableClass"),
        ]:
            response = build_response(404)
            response.request.body = body

            with self.assertLogs(logger=LOGGER) as log_manager:
                try:
                    self.client.process_response(response)
                except StoreApiResponseError:
                    self.assertEqual(1, len(log_manager.records))
                    record_request = cast(
                        Dict[str, str],
                        log_manager.records[0].__dict__.get("request", {}),
                    )
                    record_response = cast(
                        Dict[str, str | int],
                        log_manager.records[0].__dict__.get("response", {}),
                    )
                    self.assertIn(expected_log, record_request["body"])
                    self.assertEqual(SAMPLE_URL, record_response["url"])
                    self.assertEqual(404, record_response["status"])

    def test_process_response_ok(self):
        response = build_response(200)
        with self.assertNoLogs(logger=LOGGER):
            self.client.process_response(response)
