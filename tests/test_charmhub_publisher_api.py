from os import getenv

from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.stores.charmstore import CharmPublisher

publisher_auth = getenv("PUBLISHER_MACAROON", "secret")


class CharmPublisherTest(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Macaroons"]}

    def setUp(self):
        self.client = CharmPublisher()
        return super().setUp()

    def test_get_macaroon(self):
        macaroon = self.client.get_macaroon()
        self.assertIsInstance(macaroon, str)

    def test_whoami(self):
        """
        Check whoami response
        """
        response = self.client.whoami(publisher_auth)
        self.assertEqual(response["username"], "jkfran")

    def test_get_account_packages(self):
        """
        Check get_account_packages response
        """
        response = self.client.get_account_packages(publisher_auth)
        test_charm = response["charms"][0]
        self.assertEqual(test_charm["name"], "fran-test")
        self.assertEqual(test_charm["package-type"], "charm")
