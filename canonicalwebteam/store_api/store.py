from canonicalwebteam.store_api.exceptions import (
    StoreApiConnectionError,
    StoreApiResourceNotFound,
    StoreApiResponseDecodeError,
    StoreApiResponseError,
    StoreApiResponseErrorList,
)


class Store:
    def __init__(self, session, store=None):
        self.config = {1: {"base_url": "", "headers": {}}}
        self.session = session

    def process_response(self, response):
        # 5xx responses are not in JSON format
        if response.status_code >= 500:
            raise StoreApiConnectionError("Service Unavailable")

        try:
            body = response.json()
        except ValueError as decode_error:
            raise StoreApiResponseDecodeError(
                "JSON decoding failed: {}".format(decode_error)
            )

        if not response.ok:
            if "error_list" in body or "error-list" in body:
                # V1 and V2 error handling
                error_list = (
                    body["error_list"]
                    if "error_list" in body
                    else body["error-list"]
                )

                for error in error_list:
                    if error["code"] == "resource-not-found":
                        raise StoreApiResourceNotFound

                raise StoreApiResponseErrorList(
                    "The API returned a list of errors",
                    response.status_code,
                    error_list,
                )
            else:
                raise StoreApiResponseError(
                    "Unknown error from API", response.status_code
                )

        if "_embedded" in body:
            body["results"] = body["_embedded"]["clickindex:package"]
            del body["_embedded"]

        return body

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
