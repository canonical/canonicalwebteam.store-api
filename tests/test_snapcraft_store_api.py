from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.stores.snapcraft import SnapcraftStoreApi


class SnapcraftApiTest(VCRTestCase):
    def setUp(self):
        # configure self.attribute
        self.client = SnapcraftStoreApi()
        return super(SnapcraftApiTest, self).setUp()

    def test_get_all_items(self):
        result = self.client.get_all_items(size=16, api_version=1)
        snaps = result["_embedded"]["clickindex:package"]
        self.assertEqual(len(snaps), 16)

        # Test different size
        result = self.client.get_all_items(size=4, api_version=1)
        snaps = result["_embedded"]["clickindex:package"]
        self.assertEqual(len(snaps), 4)
        [self.assertIn("snap_id", snap) for snap in snaps]

    def test_get_category_items(self):
        result = self.client.get_category_items(
            category="security", size=10, page=1, api_version=1
        )
        snaps = result["_embedded"]["clickindex:package"]

        self.assertEqual(len(snaps), 10)

        for snap in snaps:
            sections = [i["name"] for i in snap["sections"]]
            self.assertIn("security", sections)

        # Test different size and category
        result = self.client.get_category_items(
            category="server-and-cloud", size=2, page=1, api_version=1
        )
        snaps = result["_embedded"]["clickindex:package"]

        self.assertEqual(len(snaps), 2)

        for snap in snaps:
            sections = [i["name"] for i in snap["sections"]]
            self.assertIn("server-and-cloud", sections)

    def test_get_featured_items(self):
        result = self.client.get_featured_items(size=10, page=1, api_version=1)
        snaps = result["_embedded"]["clickindex:package"]
        self.assertEqual(len(snaps), 10)

        # Test different size
        result = self.client.get_featured_items(size=3, page=1, api_version=1)
        snaps = result["_embedded"]["clickindex:package"]
        self.assertEqual(len(snaps), 3)

        # Test that snaps are featured
        for snap in snaps:
            sections = [i["name"] for i in snap["sections"]]
            self.assertIn("featured", sections)

    def test_get_publisher_items(self):
        result = self.client.get_publisher_items(
            publisher="28zEonXNoBLvIB7xneRbltOsp0Nf7DwS", api_version=1
        )
        snaps = result["_embedded"]["clickindex:package"]
        [self.assertEqual("jetbrains", snap["publisher"]) for snap in snaps]

        # Test different publisher
        result = self.client.get_publisher_items(
            publisher="2rsYZu6kqYVFsSejExu4YENdXQEO40Xb", api_version=1
        )
        snaps = result["_embedded"]["clickindex:package"]
        [self.assertEqual("KDE", snap["publisher"]) for snap in snaps]

    def test_get_item_details(self):
        snap = self.client.get_item_details(name="toto", api_version=2)
        self.assertIn("snap-id", snap)
        self.assertEqual("toto", snap["name"])

        # Test different snap
        snap = self.client.get_item_details(name="hello", api_version=2)
        self.assertIn("snap-id", snap)
        self.assertEqual("hello", snap["name"])

    def test_get_public_metrics(self):
        metric = "weekly_installed_base_by_country_percent"
        payload = [
            {
                "metric_name": metric,
                "snap_id": "kJWM6jE26DiyziWpGNKtedvNlmC1mbIi",
                "start": "2019-12-18",
                "end": "2019-12-18",
            }
        ]

        result = self.client.get_public_metrics(json=payload, api_version=1)

        self.assertEqual(
            "weekly_installed_base_by_country_percent",
            result[0]["metric_name"],
        )

        self.assertEqual(
            "kJWM6jE26DiyziWpGNKtedvNlmC1mbIi", result[0]["snap_id"]
        )

        self.assertEqual("2019-12-18", result[0]["buckets"][0])

        # Test different metrics
        metric = "weekly_installed_base_by_operating_system_normalized"
        payload = [
            {
                "metric_name": metric,
                "snap_id": "mVyGrEwiqSi5PugCwyH7WgpoQLemtTd6",
                "start": "2019-12-01",
                "end": "2019-12-31",
            }
        ]

        result = self.client.get_public_metrics(json=payload, api_version=1)

        self.assertEqual(
            "weekly_installed_base_by_operating_system_normalized",
            result[0]["metric_name"],
        )

        self.assertEqual(
            "mVyGrEwiqSi5PugCwyH7WgpoQLemtTd6", result[0]["snap_id"]
        )

        self.assertEqual("2019-12-01", result[0]["buckets"][0])

    def test_get_categories(self):
        result = self.client.get_categories(api_version=1)
        categories = result["_embedded"]["clickindex:sections"]

        for category in categories:
            self.assertIn("name", category)
