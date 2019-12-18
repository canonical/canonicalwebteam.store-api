from urllib.parse import urlencode
from vcr_unittest import VCRTestCase
from canonicalwebteam.store_api.stores.snapcraft import SnapcraftStoreApi


class SnapcraftApiTest(VCRTestCase):
    def setUp(self):
        # configure self.attribute
        self.client = SnapcraftStoreApi()
        return super(SnapcraftApiTest, self).setUp()

    def test_get_all_items(self):
        self.client.get_all_items(size=16, api_version=1)

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(
            self.cassette.requests[0].url,
            "https://api.snapcraft.io/api/v1/snaps/search?scope=wide&size=16",
        )
        self.assertEqual(
            self.cassette.requests[0].headers["X-Ubuntu-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)

    def test_get_category_items(self):
        self.client.get_category_items(
            category="security", size=10, page=1, api_version=1
        )

        url = "".join(
            [
                "https://api.snapcraft.io/api/v1/snaps/",
                "search",
                "?",
                urlencode(
                    {
                        "q": "",
                        "size": 10,
                        "page": 1,
                        "scope": "wide",
                        "arch": "wide",
                        "confinement": "strict,classic",
                        "fields": ",".join(
                            [
                                "package_name",
                                "title",
                                "summary",
                                "icon_url",
                                "media",
                                "publisher",
                                "developer_validation",
                                "origin",
                                "apps",
                            ]
                        ),
                        "section": "security",
                    }
                ),
            ]
        )

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(self.cassette.requests[0].url, url)
        self.assertEqual(
            self.cassette.requests[0].headers["X-Ubuntu-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)

    def test_get_featured_items(self):
        self.client.get_featured_items(size=10, page=1, api_version=1)

        url = "".join(
            [
                "https://api.snapcraft.io/api/v1/snaps/",
                "search",
                "?",
                urlencode(
                    {
                        "q": "",
                        "size": 10,
                        "page": 1,
                        "scope": "wide",
                        "arch": "wide",
                        "confinement": "strict,classic",
                        "fields": ",".join(
                            [
                                "package_name",
                                "title",
                                "summary",
                                "icon_url",
                                "media",
                                "publisher",
                                "developer_validation",
                                "origin",
                                "apps",
                            ]
                        ),
                        "section": "featured",
                    }
                ),
            ]
        )

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(self.cassette.requests[0].url, url)
        self.assertEqual(
            self.cassette.requests[0].headers["X-Ubuntu-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)

    def test_get_publisher_items(self):
        self.client.get_publisher_items(
            publisher="28zEonXNoBLvIB7xneRbltOsp0Nf7DwS",
            size=500,
            page=1,
            api_version=1,
        )

        url = "".join(
            [
                "https://api.snapcraft.io/api/v1/snaps/",
                "search",
                "?",
                urlencode(
                    {
                        "q": "publisher:28zEonXNoBLvIB7xneRbltOsp0Nf7DwS",
                        "size": 500,
                        "page": 1,
                        "scope": "wide",
                        "arch": "wide",
                        "confinement": "strict,classic",
                        "fields": ",".join(
                            [
                                "package_name",
                                "title",
                                "summary",
                                "icon_url",
                                "media",
                                "publisher",
                                "developer_validation",
                                "origin",
                                "apps",
                            ]
                        ),
                    }
                ),
            ]
        )

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(self.cassette.requests[0].url, url)
        self.assertEqual(
            self.cassette.requests[0].headers["X-Ubuntu-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)

    def test_get_item_details(self):
        self.client.get_item_details(name="toto", api_version=2)

        url = "".join(
            [
                "https://api.snapcraft.io/v2/snaps/",
                "info/toto",
                "?",
                urlencode(
                    {
                        "fields": ",".join(
                            [
                                "title",
                                "summary",
                                "description",
                                "license",
                                "contact",
                                "website",
                                "publisher",
                                "prices",
                                "media",
                                "download",
                                "version",
                                "created-at",
                                "confinement",
                                "categories",
                                "trending",
                            ]
                        )
                    }
                ),
            ]
        )

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(self.cassette.requests[0].url, url)
        self.assertEqual(
            self.cassette.requests[0].headers["Snap-Device-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)

    def test_get_public_metrics(self):
        payload = [
            {
                "metric_name": "weekly_installed_base_by_country_percent",
                "snap_id": "kJWM6jE26DiyziWpGNKtedvNlmC1mbIi",
                "start": "2019-12-18",
                "end": "2019-12-18",
            }
        ]
        self.client.get_public_metrics(json=payload, api_version=1)

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(
            self.cassette.requests[0].url,
            "https://api.snapcraft.io/api/v1/snaps/metrics",
        )
        self.assertEqual(
            self.cassette.requests[0].headers["X-Ubuntu-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)

    def test_get_categories(self):
        self.client.get_categories(api_version=1)

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(
            self.cassette.requests[0].url,
            "https://api.snapcraft.io/api/v1/snaps/sections",
        )
        self.assertEqual(
            self.cassette.requests[0].headers["X-Ubuntu-Series"], "16"
        )
        self.assertEqual(self.cassette.responses[0]["status"]["code"], 200)
