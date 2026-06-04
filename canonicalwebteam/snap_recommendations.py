from os import getenv
from urllib.parse import urlparse

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

    def get_service_root_url(self) -> str:
        """
        Return recommendation service root URL outside the /api path.
        """
        parsed = urlparse(self.base_url)
        path = parsed.path.rstrip("/")
        if path.endswith("/api"):
            path = path[: -len("/api")]
        root_path = f"{path}/" if path else "/"
        sanitized = parsed._replace(
            path=root_path,
            params="",
            query="",
            fragment="",
        )
        return sanitized.geturl()

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

    def get_featured_snaps(self) -> list:
        """
        Return featured snaps.

        Endpoint: [GET] /featured
        """
        url = f"{self.get_service_root_url()}featured"
        response = self.session.get(url)
        featured_snaps = self._process_response(response)

        # Normalize to the compact featured-snaps contract expected by callers.
        return [
            {
                "details": {
                    "name": snap.get("package_name", ""),
                    "icon": snap.get("icon_url", ""),
                    "title": snap.get("title", ""),
                    "publisher": snap.get("developer_name", ""),
                    "developer_validation": snap.get(
                        "developer_validation", ""
                    ),
                    "summary": snap.get("summary", ""),
                },
            }
            for snap in featured_snaps
        ]

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
