from unittest import TestCase
from semver import parse
from canonicalwebteam.store_api import __version__


class StoreApiTest(TestCase):
    def test_version(self):
        self.assertTrue(parse(__version__))
