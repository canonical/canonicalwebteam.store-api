from vcr_unittest import VCRTestCase

from canonicalwebteam.snap_recommendations import SnapRecommendation


class SnapRecommendationTest(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {"filter_headers": ["Authorization", "Macaroons"]}

    def setUp(self):
        self.client = SnapRecommendation()
        return super().setUp()

    def test_get_categories(self):
        response = self.client.get_categories()
        self.assertIsInstance(response, list)
        if len(response) > 0:
            category = response[0]
            self.assertIn("id", category)
            self.assertIn("name", category)
            self.assertIn("description", category)

    def test_get_category_popular(self):
        response = self.client.get_category("popular")
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("rank", snap)
            self.assertIn("details", snap)
            details = snap["details"]
            self.assertIn("name", details)
            self.assertIn("title", details)

    def test_get_category_recent(self):
        response = self.client.get_category("recent")
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("details", snap)
            self.assertIn("name", snap["details"])

    def test_get_category_trending(self):
        response = self.client.get_category("trending")
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("details", snap)
            self.assertIn("name", snap["details"])

    def test_get_category_top_rated(self):
        response = self.client.get_category("top_rated")
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("details", snap)
            self.assertIn("name", snap["details"])

    def test_get_popular(self):
        response = self.client.get_popular()
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("rank", snap)
            self.assertIn("details", snap)

    def test_get_recent(self):
        response = self.client.get_recent()
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("details", snap)

    def test_get_trending(self):
        response = self.client.get_trending()
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("details", snap)

    def test_get_top_rated(self):
        response = self.client.get_top_rated()
        self.assertIsInstance(response, list)
        if len(response) > 0:
            snap = response[0]
            self.assertIn("snap_id", snap)
            self.assertIn("details", snap)

    def test_get_recently_updated_default(self):
        response = self.client.get_recently_updated()
        self.assertIsInstance(response, dict)
        self.assertIn("snaps", response)
        self.assertIn("page", response)
        self.assertIn("size", response)
        self.assertEqual(response["page"], 1)
        self.assertEqual(response["size"], 10)
        self.assertIsInstance(response["snaps"], list)
        if len(response["snaps"]) > 0:
            snap = response["snaps"][0]
            self.assertIn("name", snap)
            self.assertIn("snap_id", snap)

    def test_get_recently_updated_custom_pagination(self):
        response = self.client.get_recently_updated(page=2, size=5)
        self.assertIsInstance(response, dict)
        self.assertIn("snaps", response)
        self.assertIn("page", response)
        self.assertIn("size", response)
        self.assertEqual(response["page"], 2)
        self.assertEqual(response["size"], 5)
        self.assertIsInstance(response["snaps"], list)
        self.assertEqual(len(response["snaps"]), 5)

    def test_get_recently_updated_large_size(self):
        response = self.client.get_recently_updated(page=1, size=20)
        self.assertIsInstance(response, dict)
        self.assertIn("snaps", response)
        self.assertEqual(response["page"], 1)
        self.assertEqual(response["size"], 20)
        self.assertLessEqual(len(response["snaps"]), 20)
