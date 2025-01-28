from os import getenv

from requests import Session
from canonicalwebteam.store_api.base import Base


DEVICEGW_URL = getenv("DEVICEGW_URL", "https://api.snapcraft.io/")


class DeviceGW(Base):
    def __init__(self, session=Session(), store=None):
        super().__init__(session)
        self.config = {
            1: {
                "base_url": f"{DEVICEGW_URL}api/v1/snaps/",
                "headers": {"X-Ubuntu-Series": "16"},
            },
            2: {
                "base_url": f"{DEVICEGW_URL}v2/snaps/",
                "headers": {"Snap-Device-Series": "16"},
            },
        }

        if store:
            self.config[1]["headers"].update({"X-Ubuntu-Store": store})
            self.config[2]["headers"].update({"Snap-Device-Store": store})

    def get_endpoint_url(self, endpoint, api_version=1):
        base_url = self.config[api_version]["base_url"]
        return f"{base_url}{endpoint}"

    def search(
        self,
        search,
        size=100,
        page=1,
        category=None,
        arch="wide",
        api_version=1,
    ):
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snap_search
        Endpoint:  https://api.snapcraft.io/api/v1/snaps/search
        """
        url = self.get_endpoint_url("search", api_version)
        headers = self.config[api_version].get("headers")

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
        query="",
        category="",
        architecture="",
        publisher="",
        featured="false",
        fields=[],
    ):
        """
        Documentation: https://api.snapcraft.io/docs/search.html#snaps_find
        Endpoint: [GET] https://api.snapcraft.io/v2/snaps/find
        """
        url = self.get_endpoint_url("find", 2)
        headers = self.config[2].get("headers")
        params = {
            "q": query,
            "category": category,
            "architecture": architecture,
            "publisher": publisher,
            "featured": featured,
        }
        if fields:
            params["fields"] = ",".join(fields)
        response = self.session.get(url, params=params, headers=headers)
        return self.process_response(response)

    def get_all_items(self, size, api_version=1):
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

    def get_category_items(self, category, size=10, page=1, api_version=1):
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

    def get_featured_items(self, size=10, page=1, api_version=1):
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

    def get_publisher_items(self, publisher, size=500, page=1, api_version=1):
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

    def get_item_details(self, name, channel=None, fields=[], api_version=2):
        """
        Documentation: https://api.snapcraft.io/docs/info.html
        Endpoint: [GET]
            https://api.snapcraft.io/api/v2/{name_space}/info/{package_name}
        """
        url = self.get_endpoint_url("info/" + name, api_version)
        params = {"fields": ",".join(fields)}

        if channel:
            params["channel"] = channel

        return self.process_response(
            self.session.get(
                url,
                params=params,
                headers=self.config[api_version].get("headers"),
            )
        )

    def get_public_metrics(self, json, api_version=1):
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

    def get_categories(self, api_version=2, type="shared"):
        """
        Documentation: https://api.snapcraft.io/docs/categories.html
        Endpoint: https://api.snapcraft.io/api/v2/{name_space}/categories
        """
        url = self.get_endpoint_url("categories", api_version)
        return self.process_response(
            self.session.get(
                url,
                headers=self.config[api_version].get("headers"),
                params={"type": type},
            )
        )

    def get_resource_revisions(self, name, resource_name, api_version=2):
        """
        Documentation:
            https://api.snapcraft.io/docs/charms.html#list_resource_revisions
        Endpoint:
            https://api.snapcraft.io/api/v2/charms/resources/{package_name}/{resource_name}/revisions
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

    def get_featured_snaps(self, api_version=1, fields="snap_id"):
        """
        Documentation: (link to spec)
            https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8/edit
        Endpoint: https://api.snapcraft.io/api/v1/snaps/search
        """
        url = self.get_endpoint_url("search")
        headers = self.config[api_version].get("headers")

        params = {
            "scope": "wide",
            "arch": "wide",
            "confinement": "strict,classic,devmode",
            "fields": fields,
            "section": "featured",
        }

        return self.process_response(
            self.session.get(url, params=params, headers=headers)
        )
