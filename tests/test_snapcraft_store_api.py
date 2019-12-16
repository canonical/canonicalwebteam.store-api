from datetime import datetime
from canonicalwebteam.store_api.stores.snapcraft import SnapcraftStoreApi


class Test:
    def setup_method(self, test_method):
        # configure self.attribute
        self.client = SnapcraftStoreApi()

    def test_get_endpoint_v1_url(self):
        url = self.client.get_endpoint_url(endpoint="search", api_version=1)
        assert url == "https://api.snapcraft.io/api/v1/snaps/search"

    def test_get_endpoint_v2_url(self):
        url = self.client.get_endpoint_url(endpoint="info", api_version=2)
        assert url == "https://api.snapcraft.io/v2/snaps/info"

    def test_headers(self):
        # API Headers for v1
        assert self.client.config[1]["headers"] == {"X-Ubuntu-Series": "16"}
        # API Headers for v2
        assert self.client.config[2]["headers"] == {"Snap-Device-Series": "16"}

    def test_get_all_items(self):
        response = self.client.get_all_items(size=16, api_version=1)
        assert isinstance(response, dict)

    def test_get_category_items(self):
        response = self.client.get_category_items(
            category="security", size=10, page=1, api_version=1
        )
        assert isinstance(response, dict)

    def test_get_featured_items(self):
        response = self.client.get_featured_items(
            size=10, page=1, api_version=1
        )
        assert isinstance(response, dict)

    def test_get_publisher_items(self):
        response = self.client.get_publisher_items(
            publisher="28zEonXNoBLvIB7xneRbltOsp0Nf7DwS",
            size=500,
            page=1,
            api_version=1,
        )
        assert isinstance(response, dict)

    def test_get_item_details(self):
        response = self.client.get_item_details(name="toto", api_version=2)
        assert isinstance(response, dict)

    def test_get_public_metrics(self):
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        payload = [
            {
                "metric_name": "weekly_installed_base_by_country_percent",
                "snap_id": "kJWM6jE26DiyziWpGNKtedvNlmC1mbIi",
                "start": date,
                "end": date,
            },
        ]
        response = self.client.get_public_metrics(json=payload, api_version=1)
        assert isinstance(response, list)

    def test_get_categories(self):
        response = self.client.get_categories(api_version=1)
        assert isinstance(response, dict)
