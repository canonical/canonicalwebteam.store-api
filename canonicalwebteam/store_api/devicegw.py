from os import getenv
from typing import Optional
from requests import Session
from canonicalwebteam.store_api.base import Base


DEVICEGW_URL = getenv("DEVICEGW_URL", "https://api.snapcraft.io/")
DEVICEGW_URL_STAGING = getenv(
    "DEVICEGW_URL_STAGING", "https://api.staging.snapcraft.io/"
)


class DeviceGW(Base):
    def __init__(
        self, namespace, session=Session(), store=None, staging=False
    ):
        super().__init__(session)
        if staging:
            self.config = {
                1: {
                    "base_url": f"{DEVICEGW_URL_STAGING}api/v1/{namespace}s/",
                    "headers": {"X-Ubuntu-Series": "16"},
                },
                2: {
                    "base_url": f"{DEVICEGW_URL_STAGING}v2/{namespace}s/",
                    "headers": {"Snap-Device-Series": "16"},
                },
            }
        else:
            self.config = {
                1: {
                    "base_url": f"{DEVICEGW_URL}api/v1/{namespace}s/",
                    "headers": {"X-Ubuntu-Series": "16"},
                },
                2: {
                    "base_url": f"{DEVICEGW_URL}v2/{namespace}s/",
                    "headers": {"Snap-Device-Series": "16"},
                },
            }

        if store:
            self.config[1]["headers"].update({"X-Ubuntu-Store": store})
            self.config[2]["headers"].update({"Snap-Device-Store": store})

    def get_endpoint_url(self, endpoint, api_version=1) -> str:
        base_url = self.config[api_version]["base_url"]
        return f"{base_url}{endpoint}"

    def search(
        self,
        search: str,
        size: int = 100,
        page: int = 1,
        category: Optional[str] = None,
        arch: str = "wide",
        api_version: int = 1,
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snap_search
        Endpoint:  https://api.snapcraft.io/api/v1/snaps/search
        """
        url = self.get_endpoint_url("search", api_version)
        headers = self.config[api_version].get("headers", {}).copy()

        if "publisher:" not in search:
            search = search.replace(":", " ")

        params = {
            "q": search,
            "size": size,
            "page": page,
            "scope": "wide",
            "confinement": "strict,classic",
            "fields": ",".join(
                [
                    "package_name",
                    "title",
                    "summary",
                    "architecture",
                    "media",
                    "developer_name",
                    "developer_id",
                    "developer_validation",
                    "origin",
                    "apps",
                    "sections",
                ]
            ),
        }

        # Arch behaves a bit oddly, but these two together should cover
        # all bases. That is: "X-Ubuntu-Architecture" header will be used
        # if present, and "arch" will be ignored *unless* "arch" == "wide".
        # "wide" doesn't work in "X-Ubuntu-Architecture", but it doesn't
        # matter because if "arch" == "wide" then "X-Ubuntu-Architecture"
        # is ignored and all architectures are returned
        # See: https://api.snapcraft.io/docs/search.html#snap_search
        headers["X-Ubuntu-Architecture"] = arch
        params["arch"] = arch

        if category:
            params["section"] = category

        return self.process_response(
            self.session.get(url, params=params, headers=headers)
        )

    def find(
        self,
        query: str = "",
        category: str = "",
        architecture: str = "",
        publisher: str = "",
        featured: str = "",
        fields: list = [],
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snaps_find
        Endpoint: [GET] https://api.snapcraft.io/v2/{namespace}/find
        """
        url = self.get_endpoint_url("find", 2)
        headers = self.config[2].get("headers")
        params = {"q": query}
        if fields:
            params["fields"] = ",".join(fields)
        if architecture:
            params["architecture"] = architecture
        if category:
            params["category"] = category
        if publisher:
            params["publisher"] = publisher
        if featured:
            params["featured"] = featured
        response = self.session.get(url, params=params, headers=headers)
        return self.process_response(response)

    def get_all_items(self, size: int, api_version: int = 1) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snap_search
        Endpoint:  https://api.snapcraft.io/api/v1/snaps/search
        """
        url = self.get_endpoint_url("search", api_version)

        return self.process_response(
            self.session.get(
                url,
                params={"scope": "wide", "size": size},
                headers=self.config[api_version].get("headers"),
            )
        )

    def get_category_items(
        self,
        category: str,
        size: int = 10,
        page: int = 1,
        api_version: int = 1,
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snap_search
        Endpoint:  https://api.snapcraft.io/api/v1/snaps/search
        """
        return self.search(
            search="",
            category=category,
            size=size,
            page=page,
            api_version=api_version,
        )

    def get_featured_items(
        self, size: int = 10, page: int = 1, api_version: int = 1
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snap_search
        Endpoint:  https://api.snapcraft.io/api/v1/snaps/search
        """
        return self.search(
            search="",
            category="featured",
            size=size,
            page=page,
            api_version=api_version,
        )

    def get_publisher_items(
        self,
        publisher: str,
        size: int = 500,
        page: int = 1,
        api_version: int = 1,
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snap_search
        Endpoint:  https://api.snapcraft.io/api/v1/snaps/search
        """
        return self.search(
            search="publisher:" + publisher,
            size=size,
            page=page,
            api_version=api_version,
        )

    def get_item_details(
        self,
        name: str,
        channel: Optional[str] = None,
        fields: list = [],
        api_version: int = 2,
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/info.html
        Endpoint: [GET]
            https://api.snapcraft.io/v2/{name_space}/info/{package_name}
        """
        url = self.get_endpoint_url("info/" + name, api_version)
        params = {}
        if fields:
            params = {"fields": ",".join(fields)}
        headers = self.config[api_version].get("headers")

        if channel:
            params["channel"] = channel
        response = self.session.get(
            url,
            params=params,
            headers=headers,
        )
        return self.process_response(response)

    def get_snap_details(
        self,
        name: str,
        channel: Optional[str] = None,
        fields: list = [],
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/details.html#snap_details
        Endpoint: [GET]
            https://api.snapcraft.io/api/v1/{name_space}/details/{package_name}
        """
        # this method is only available in API version 1
        api_version = 1
        url = self.get_endpoint_url("details/" + name, api_version=api_version)
        params = {}
        if fields:
            params = {"fields": ",".join(fields)}
        # Having an empty channel string tells details endpoint to
        # not filter by channel. Having None and not including the channel
        # parameter makes the endpoint default to latest/stable channel
        if channel is not None:
            params["channel"] = channel
        headers = self.config[api_version].get("headers")

        response = self.session.get(
            url,
            params=params,
            headers=headers,
        )
        return self.process_response(response)

    def get_public_metrics(self, json: dict, api_version: int = 1) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/metrics.html
        Endpoint: https://api.snapcraft.io/api/v1/snaps/metrics
        """
        url = self.get_endpoint_url("metrics")

        headers = self.config[api_version].get("headers", {})
        headers.update({"Content-Type": "application/json"})

        return self.process_response(
            self.session.post(url, headers=headers, json=json)
        )

    def get_categories(
        self, api_version: int = 2, type: str = "shared"
    ) -> dict:
        """
        Documentation: https://api.snapcraft.io/docs/categories.html
        Endpoint: https://api.snapcraft.io/v2/{name_space}/categories
        """
        url = self.get_endpoint_url("categories", api_version)
        return self.process_response(
            self.session.get(
                url,
                headers=self.config[api_version].get("headers"),
                params={"type": type},
            )
        )

    def get_resource_revisions(
        self, name: str, resource_name: str, api_version: int = 2
    ) -> dict:
        """
        Documentation:
            https://api.snapcraft.io/docs/charms.html#list_resource_revisions
        Endpoint:
            https://api.snapcraft.io/v2/charms/resources/{package_name}/{resource_name}/revisions
        """
        url = self.get_endpoint_url(
            f"resources/{name}/{resource_name}/revisions", api_version
        )

        return self.process_response(
            self.session.get(
                url,
                headers=self.config[api_version].get("headers"),
            )
        )["revisions"]

    def get_featured_snaps(
        self, api_version: int = 1, fields: str = "snap_id", headers: dict = {}
    ) -> dict:
        """
        Documentation: (link to spec)
            https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8/edit
        Endpoint: https://api.snapcraft.io/api/v1/snaps/search
        """
        url = self.get_endpoint_url("search")
        default_headers = self.config[api_version].get("headers", {})

        merged_headers = {**default_headers, **headers}

        params = {
            "scope": "wide",
            "arch": "wide",
            "confinement": "strict,classic,devmode",
            "fields": fields,
            "section": "featured",
        }

        return self.process_response(
            self.session.get(url, params=params, headers=merged_headers)
        )
