
from unittest.mock import Mock
from os import getenv
from pprint import pprint

from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.stores.snapstore import SnapStoreAdmin 

test_session = getenv("DEVELOPER_TOKEN", {"developer_token": "secret"})

class SnapPublisherTest(VCRTestCase):

    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Macaroon", "developer_token"]}

    def setUp(self):
        self.client = SnapStoreAdmin()
        return super().setUp()

    def test_delete_featured_snaps(self):
        mock_session = Mock()
        self.client._get_publisherwg_authorization_header = Mock(
            return_value={"Authorization": "Macaroon some_random_macaroon"}
        )
        
        mock__response = Mock()
        mock__response.status_code = 201
        mock_session.delete.return_value = mock__response
        payload = {
                "packages": [
                "12345"
            ],
        }
        response = self.client.delete_featured_snaps(
            mock_session, payload
        )
        pprint(response.json())
        self.assertEqual(response.status_code, 201)

    def test_get_featured_snaps(self):
        response = self.client.get_featured_snaps(test_session)
        self.assertIn("_embedded", response)