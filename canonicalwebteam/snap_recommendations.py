from os import getenv

from requests import Session


RECOMMENDATIONS_API_URL = getenv(
    "SNAP_RECOMMENDATIONS_API_URL",
    "https://recommendations.snapcraft.io/api/",
)


class SnapRecommendations:
    """Helpers for Snap Recommendation Service."""

    def __init__(self, session=Session()):
        self.session = session
        self.base_url = RECOMMENDATIONS_API_URL

    def get_endpoint_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def _process_response(self, response):
        """
        Process the response from the recommendation service.
        Raises an HTTPError if the request was not successful.
        """
        response.raise_for_status()
        return response.json()

    def get_categories(self) -> list:
        """
        Return the list of recommendation categories.

        Endpoint: [GET] /categories
        """
        url = self.get_endpoint_url("categories")
        response = self.session.get(url)
        return self._process_response(response)

    def get_category(self, category_id: str) -> list:
        """
        Return ranked snaps for a given category.

        Endpoint: [GET] /category/{id}
        """
        url = self.get_endpoint_url(f"category/{category_id}")
        response = self.session.get(url)
        return self._process_response(response)

    def get_popular(self) -> list:
        return self.get_category("popular")

    def get_recent(self) -> list:
        return self.get_category("recent")

    def get_trending(self) -> list:
        return self.get_category("trending")

    def get_top_rated(self) -> list:
        return self.get_category("top_rated")

    def get_recently_updated(
        self, page: int = 1, size: int = 10, timeout: int = 10
    ) -> dict:
        """
        Return recently updated snaps with pagination.

        Endpoint: [GET] /recently-updated?page=<page>&size=<size>
        Returns: { "page": n, "size": n, "snaps": [ ... ] }
        """
        params = {"page": page, "size": size}
        url = self.get_endpoint_url("recently-updated")
        response = self.session.get(url, params=params, timeout=timeout)
        return self._process_response(response)
