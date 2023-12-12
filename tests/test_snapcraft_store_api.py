from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.stores.snapstore import SnapStore
from canonicalwebteam.store_api.exceptions import StoreApiResourceNotFound


class SnapStoreTest(VCRTestCase):
    def setUp(self):
        # configure self.attribute
        self.client = SnapStore()
        return super(SnapStoreTest, self).setUp()

    def test_search_size(self):
        """
        Check we can specify the number of search results
        """

        result_default = self.client.search("code")
        result_10 = self.client.search("code", size=10)
        result_100 = self.client.search("code", size=100)
        result_300 = self.client.search("code", size=300)

        # The total should be always the same
        self.assertEqual(result_300["total"], result_10["total"])

        self.assertEqual(len(result_default["results"]), 100)
        self.assertEqual(len(result_10["results"]), 10)
        self.assertEqual(len(result_100["results"]), 100)
        # 250 is the maximum the API return
        self.assertEqual(len(result_300["results"]), 250)

    def test_search_by_arch(self):
        """
        Check we can search for snaps and filter by architecture
        """

        # Test default behaviour to be arch="wide"
        result_default = self.client.search("test-snap-amd64")
        result_wide = self.client.search("test-snap-amd64", arch="wide")

        self.assertEqual(result_default["total"], result_wide["total"])

        # "test-snap-amd64" is only found in amd64
        result_amd64 = self.client.search("test-snap-amd64", 1, arch="amd64")
        result_i386 = self.client.search("test-snap-amd64", 1, arch="i386")

        self.assertEqual(result_amd64["total"], 1)
        self.assertEqual(result_i386["total"], 0)

        # "test-snap-i386" is only found in i386
        result_amd64 = self.client.search("test-snap-i386", 1, arch="amd64")
        result_i386 = self.client.search("test-snap-i386", 1, arch="i386")

        self.assertEqual(result_amd64["total"], 0)
        self.assertEqual(result_i386["total"], 1)

    def test_get_all_items(self):
        result = self.client.get_all_items(size=16, api_version=1)
        self.assertEqual(len(result["results"]), 16)
        [self.assertIn("snap_id", snap) for snap in result["results"]]

        # Test different size
        result = self.client.get_all_items(size=4, api_version=1)
        self.assertEqual(len(result["results"]), 4)
        [self.assertIn("snap_id", snap) for snap in result["results"]]

    def test_get_category_items(self):
        result = self.client.get_category_items(
            category="security", size=10, page=1, api_version=1
        )

        self.assertEqual(len(result["results"]), 10)

        for snap in result["results"]:
            sections = [i["name"] for i in snap["sections"]]
            self.assertIn("security", sections)

        # Test different size and category
        result = self.client.get_category_items(
            category="server-and-cloud", size=2, page=1, api_version=1
        )

        self.assertEqual(len(result["results"]), 2)

        for snap in result["results"]:
            sections = [i["name"] for i in snap["sections"]]
            self.assertIn("server-and-cloud", sections)

    def test_get_featured_items(self):
        result = self.client.get_featured_items(size=10, page=1, api_version=1)
        self.assertEqual(len(result["results"]), 10)

        # Test different size
        result = self.client.get_featured_items(size=3, page=1, api_version=1)
        self.assertEqual(len(result["results"]), 3)

        # Test that snaps are featured
        for snap in result["results"]:
            sections = [i["name"] for i in snap["sections"]]
            self.assertIn("featured", sections)

    def test_get_publisher_items(self):
        result = self.client.get_publisher_items(
            publisher="28zEonXNoBLvIB7xneRbltOsp0Nf7DwS", api_version=1
        )

        for snap in result["results"]:
            self.assertEqual("jetbrains", snap["developer_name"])

        # Test different publisher
        result = self.client.get_publisher_items(
            publisher="2rsYZu6kqYVFsSejExu4YENdXQEO40Xb", api_version=1
        )

        for snap in result["results"]:
            self.assertEqual("KDE", snap["developer_name"])

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
        categories = self.client.get_categories(api_version=2)["categories"]

        for category in categories:
            self.assertIn("name", category)

    def test_get_featured_results(self):
        results = self.client.find(category="featured")["results"]
        self.assertIn("featured", self.cassette.requests[0].query[0])

        # there is no specific field that shows the category at the moment
        # so just testing if the returned number of results is greater than 0
        self.assertGreater(len(results), 0)

    def test_404(self):
        with self.assertRaises(StoreApiResourceNotFound):
            self.client.get_item_details(name="four-o-four", api_version=2)
