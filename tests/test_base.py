from vcr_unittest import VCRTestCase
from unittest.mock import Mock
from requests import Session
from requests.models import Response
from canonicalwebteam.store_api.base import Base
from canonicalwebteam.exceptions import (
    StoreApiInternalError,
    StoreApiNotImplementedError,
    StoreApiBadGatewayError,
    StoreApiServiceUnavailableError,
    StoreApiGatewayTimeoutError,
    StoreApiConnectionError,
)

STATUS_MAPPING = {
    500: StoreApiInternalError,
    501: StoreApiNotImplementedError,
    502: StoreApiBadGatewayError,
    503: StoreApiServiceUnavailableError,
    504: StoreApiGatewayTimeoutError,
}


def build_response(status_code: int):
    response = Mock(spec=Response)
    response.status_code = status_code
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
