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
        response = self.client.whoami(publisher_auth=publisher_auth)
        self.assertEqual(response["username"], "jkfran")

    def test_get_account_packages_all_charms(self):
        charms = self.client.get_account_packages(
            publisher_auth=publisher_auth, package_type="charm"
        )
        for charm in charms:
            self.assertEqual(charm["package-type"], "charm")

    def test_get_account_packages_registered_charms(self):
        registered_charms = self.client.get_account_packages(
            publisher_auth=publisher_auth,
            package_type="charm",
            status="registered",
        )
        for charm in registered_charms:
            self.assertEqual(charm["package-type"], "charm")
            self.assertEqual(charm["status"], "registered")

    def test_get_account_packages_published_charms(self):
        published_charms = self.client.get_account_packages(
            publisher_auth=publisher_auth,
            package_type="charm",
            status="published",
        )
        for charm in published_charms:
            self.assertEqual(charm["package-type"], "charm")
            self.assertEqual(charm["status"], "published")
