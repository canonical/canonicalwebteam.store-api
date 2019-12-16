from canonicalwebteam.store_api.exceptions import (
    StoreApiResponseDecodeError,
    StoreApiResponseError,
    StoreApiResponseErrorList,
)


class StoreApi:
    def __init__(self, session, store=None):
        self.config = {1: {"base_url": "", "headers": {}}}
        self.session = session

    def process_response(self, response):
        try:
            body = response.json()
        except ValueError as decode_error:
            api_error_exception = StoreApiResponseDecodeError(
                "JSON decoding failed: {}".format(decode_error)
            )
            raise api_error_exception

        if not response.ok:
            if "error_list" in body or "error-list" in body:
                # V1 and V2 error handling
                error_body = (
                    body["error_list"]
                    if "error_list" in body
                    else body["error-list"]
                )
                api_error_exception = StoreApiResponseErrorList(
                    "The API returned a list of errors",
                    response.status_code,
                    error_body,
                )
                raise api_error_exception
            else:
                raise StoreApiResponseError(
                    "Unknown error from API", response.status_code
                )

        return body

    def get_endpoint_url(self, endpoint, api_version=1):
        base_url = self.config[api_version]["base_url"]
        return f"{base_url}{endpoint}"

    def search(self, search, size, page, category=None, api_version=1):
        url = self.get_endpoint_url("search", api_version)

        params = {
            "q": search,
            "size": size,
            "page": page,
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

        if category:
            params["section"] = category

        return self.process_response(
            self.session.get(
                url,
                params=params,
                headers=self.config[api_version].get("headers"),
            )
        )

    def get_all_items(self, size, api_version=1):
        url = self.get_endpoint_url("search", api_version)

        return self.process_response(
            self.session.get(
                url,
                params={"scope": "wide", "size": size},
                headers=self.config[api_version].get("headers"),
            )
        )

    def get_category_items(self, category, size=10, page=1, api_version=1):
        return self.search(
            search="",
            category=category,
            size=size,
            page=page,
            api_version=api_version,
        )

    def get_featured_items(self, size=10, page=1, api_version=1):
        return self.search(
            search="",
            category="featured",
            size=size,
            page=page,
            api_version=api_version,
        )

    def get_publisher_items(self, publisher, size=500, page=1, api_version=1):
        return self.search(
            search="publisher:" + publisher,
            category="featured",
            size=size,
            page=page,
            api_version=api_version,
        )

    def get_item_details(self, name, api_version=1):
        url = self.get_endpoint_url("info/" + name, api_version)

        params = {
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

        return self.process_response(
            self.session.get(
                url,
                params=params,
                headers=self.config[api_version].get("headers"),
            )
        )

    def get_public_metrics(self, json, api_version=1):
        url = self.get_endpoint_url("metrics")

        headers = self.config[api_version].get("headers", {})
        headers.update({"Content-Type": "application/json"})

        return self.process_response(
            self.session.post(url, headers=headers, json=json)
        )

    def get_categories(self, api_version=1):
        url = self.get_endpoint_url("sections")

        return self.process_response(
            self.session.get(
                url, headers=self.config[api_version].get("headers")
            )
        )
