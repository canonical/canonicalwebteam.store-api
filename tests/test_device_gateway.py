from vcr_unittest import VCRTestCase

from canonicalwebteam.store_api.devicegw import DeviceGW


class DeviceGWTest(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Macaroons"]}

    def setUp(self):
        self.client = DeviceGW()
        return super().setUp()

    def test_search(self):
        response = self.client.search("xyz")
        self.assertIsInstance(response, dict)
        # self.assertIn("xyz", response)

    def test_find(self):
        response = self.client.find("xyz")
        self.assertIsInstance(response, dict)
        # self.assertIn("xyz", response)

    def test_get_all_items(self):
        response = self.client.get_all_items(5)
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response["_embedded"]["clickindex:package"]), 5)

    def test_get_category_items(self):
        response = self.client.get_category_items("games", 3)
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response["_embedded"]["clickindex:package"]), 3)

        for item in response["_embedded"]["clickindex:package"]:
            self.assertTrue(
                any("games" in section["name"] for section in item["sections"])
            )

    def test_get_featured_items(self):
        response = self.client.get_featured_items(2)
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response["_embedded"]["clickindex:package"]), 2)
        for item in response["_embedded"]["clickindex:package"]:
            self.assertTrue(
                any(
                    "featured" in section["name"]
                    for section in item["sections"]
                )
            )

    def test_get_publisher_items(self):
        response = self.client.get_publisher_items("lukewh", 3)
        self.assertIsInstance(response, dict)
        for item in response["_embedded"]["clickindex:package"]:
            self.assertEqual("canonical", item["developer_name"].lower())

    def test_get_item_details(self):
        response = self.client.get_item_details(
            "test-lukewh", fields=["name", "summary"]
        )
        self.assertIsInstance(response, dict)
        self.assertEqual(response["name"], "test-lukewh")

    def test_get_categories(self):
        response = self.client.get_categories()
        self.assertIsInstance(response, dict)
        self.assertIn("categories", response)

    def test_get_featured_snaps(self):
        response = self.client.get_featured_snaps()
        self.assertIsInstance(response, dict)
        # self.assertIn("featured", response)
