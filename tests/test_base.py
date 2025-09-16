from vcr_unittest import VCRTestCase
from unittest.mock import Mock, MagicMock
from requests import Session
from requests.models import Response, Request
from canonicalwebteam.store_api.base import (
    Base,
    logger as LOGGER,
)
from canonicalwebteam.exceptions import (
    StoreApiInternalError,
    StoreApiNotImplementedError,
    StoreApiBadGatewayError,
    StoreApiServiceUnavailableError,
    StoreApiGatewayTimeoutError,
    StoreApiConnectionError,
    StoreApiResponseError,
)

STATUS_MAPPING = {
    500: StoreApiInternalError,
    501: StoreApiNotImplementedError,
    502: StoreApiBadGatewayError,
    503: StoreApiServiceUnavailableError,
    504: StoreApiGatewayTimeoutError,
}


def build_response(status_code: int):
    # the request is used by the logging messages
    request = Mock(spec=Request)
    request.url = "http://www.test.com"
    request.headers = {}
    request._cookies = {}
    request.body = ""

    response = Mock(spec=Response)
    response.status_code = status_code
    response.headers = {}
    response.cookies = {}
    response.request = request
    response.json = MagicMock(return_value={})

    if status_code >= 400:
        response.ok = False

    return response


class BaseTest(VCRTestCase):
    def setUp(self):
        self.client = Base(Mock(spec=Session))
        return super().setUp()

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
        response = build_response(404)
        with self.assertRaises(StoreApiResponseError):
            with self.assertLogs(logger=LOGGER) as log_manager:
                self.client.process_response(response)
                self.assertEqual(
                    log_manager.records,
                    [
                        (
                            "Request: {url = http://www.test.com, "
                            "headers = {}, "
                            "cookies = dict_items([]), body = }"
                        ),
                        (
                            "Response: {status = 500, headers = {}, "
                            "cookies = dict_items([])}"
                        ),
                    ],
                )

    def test_process_response_ok(self):
        response = build_response(200)
        with self.assertNoLogs(logger=LOGGER):
            self.client.process_response(response)
