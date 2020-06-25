from os import getenv

from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.stores.charmstore import CharmPublisher

session = {"publisher-macaroon": getenv("PUBLISHER_MACAROON", "secret")}


class CharmPublisherTest(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Cookie"]}

    def setUp(self):
        self.client = CharmPublisher()
        return super().setUp()

    def test_whoami(self):
        """
        Check whoami response
        """
        response = self.client.whoami(session)
        self.assertEqual(response["username"], "jkfran")

    def test_get_account_packages(self):
        """
        Check get_account_packages response
        """
        response = self.client.get_account_packages(session)
        test_charm = response["charms"][0]
        self.assertEqual(test_charm["name"], "fran-test")
        self.assertEqual(test_charm["package-type"], "charm")
