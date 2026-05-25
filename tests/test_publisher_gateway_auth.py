import unittest
from unittest.mock import Mock

from requests import Session
from requests.models import Response

from canonicalwebteam.store_api.publishergw import PublisherGW


def make_ok_response(body):
    response = Mock(spec=Response)
    response.status_code = 200
    response.ok = True
    response.headers = {}
    response.json = Mock(return_value=body)
    return response


class TestPublisherGWAuth(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.session = Mock(spec=Session)
        self.client = PublisherGW("charm", self.session)

    def test_issue_usso_macaroon(self):
        self.session.post.return_value = make_ok_response(
            {"macaroon": "test-root"}
        )

        macaroon = self.client.issue_usso_macaroon(
            ttl=300,
            permissions=["account-view-packages"],
            channels=["stable"],
            packages=[{"type": "charm", "name": "my-charm"}],
        )

        self.assertEqual(macaroon, "test-root")
        self.session.post.assert_called_once_with(
            url=self.client.get_endpoint_url("tokens/usso"),
            json={
                "ttl": 300,
                "permissions": ["account-view-packages"],
                "channels": ["stable"],
                "packages": [{"type": "charm", "name": "my-charm"}],
            },
        )

    def test_issue_usso_macaroon_permissions_required(self):
        with self.assertRaises(ValueError):
            self.client.issue_usso_macaroon(ttl=300, permissions=[])

    def test_exchange_usso_macaroons(self):
        self.session.post.return_value = make_ok_response(
            {"macaroon": "test-auth"}
        )

        macaroon = self.client.exchange_usso_macaroons(
            root_macaroon="root-macaroon",
            discharge_macaroon="discharge-macaroon",
            client_description="charmhub.io - test-agent",
        )

        self.assertEqual(macaroon, "test-auth")
        self.session.post.assert_called_once_with(
            url=self.client.get_endpoint_url("tokens/usso/exchange"),
            headers={
                "Authorization": (
                    "Macaroon root=root-macaroon, discharge=discharge-macaroon"
                )
            },
            json={"client-description": "charmhub.io - test-agent"},
        )
