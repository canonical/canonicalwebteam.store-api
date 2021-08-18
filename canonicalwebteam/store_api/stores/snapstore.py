from os import getenv

import requests

from canonicalwebteam.store_api.store import Store
from canonicalwebteam.store_api.publisher import Publisher

SNAPSTORE_API_URL = getenv("SNAPSTORE_API_URL", "https://api.snapcraft.io/")
SNAPSTORE_DASHBOARD_API_URL = getenv(
    "SNAPSTORE_DASHBOARD_API_URL", "https://dashboard.snapcraft.io/"
)


class SnapStore(Store):
    def __init__(self, session=requests.Session(), store=None):
        super().__init__(session, store)

        self.config = {
            1: {
                "base_url": f"{SNAPSTORE_API_URL}api/v1/snaps/",
                "headers": {"X-Ubuntu-Series": "16"},
            },
            2: {
                "base_url": f"{SNAPSTORE_API_URL}v2/snaps/",
                "headers": {"Snap-Device-Series": "16"},
            },
        }

        if store:
            self.config[1]["headers"].update({"X-Ubuntu-Store": store})
            self.config[2]["headers"].update({"Snap-Device-Store": store})

    def get_item_details(
        self,
        name,
        fields=[
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
            "unlisted",
        ],
        api_version=1,
    ):
        return super(SnapStore, self).get_item_details(
            name, None, fields, api_version
        )


class SnapPublisher(Publisher):
    def __init__(self, session=requests.Session()):
        super().__init__(session)

        self.config = {
            1: {"base_url": f"{SNAPSTORE_DASHBOARD_API_URL}dev/api/"},
            2: {"base_url": f"{SNAPSTORE_DASHBOARD_API_URL}api/v2/"},
        }

    def get_macaroon(self, permissions):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
        """
        response = self.session.post(
            url=self.get_endpoint_url("tokens", 2),
            json={"permissions": permissions},
        )

        return self.process_response(response)["macaroon"]

    def whoami(self, session):
        response = self.session.get(
            url=self.get_endpoint_url("tokens/whoami", 2),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)


class SnapStoreAdmin(SnapPublisher):
    def get_endpoint_url(self, endpoint, api_version=2):
        return super().get_endpoint_url(f"stores/{endpoint}", api_version)

    def get_stores(self, session, roles=["admin", "review", "view"]):
        """Return a list a stores with the given roles

        :return: A list of stores
        """
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=super().get_endpoint_url("account", 1), headers=headers
        )

        account_info = self.process_response(response)
        stores = account_info.get("stores", [])
        user_stores = []

        for store in stores:
            if not set(roles).isdisjoint(store["roles"]):
                user_stores.append(store)

        return user_stores

    def get_store(self, session, store_id):
        """Return a store where the user is an admin

        :return: Store details
        """
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url(store_id), headers=headers
        )

        return self.process_response(response)["store"]

    def get_store_snaps(
        self, session, store_id, query=None, allowed_for_inclusion=None
    ):
        headers = self._get_authorization_header(session)
        params = {}

        if query:
            params["q"] = query

        if allowed_for_inclusion:
            params["allowed-for-inclusion"] = allowed_for_inclusion

        response = self.session.get(
            url=self.get_endpoint_url(f"{store_id}/snaps"),
            params=params,
            headers=headers,
        )

        return self.process_response(response).get("snaps", [])

    def get_store_members(self, session, store_id):
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url(f"{store_id}"),
            headers=headers,
        )

        return self.process_response(response).get("users", [])

    def update_store_members(self, session, store_id, members):
        headers = self._get_authorization_header(session)

        response = self.session.post(
            url=self.get_endpoint_url(f"{store_id}/users"),
            headers=headers,
            json=members,
        )

        return self.process_response(response)

    def invite_store_members(self, session, store_id, members):
        headers = self._get_authorization_header(session)

        response = self.session.post(
            url=self.get_endpoint_url(f"{store_id}/invites"),
            headers=headers,
            json=members,
        )

        return self.process_response(response)

    def change_store_settings(self, session, store_id, settings):
        headers = self._get_authorization_header(session)

        response = self.session.put(
            url=self.get_endpoint_url(f"{store_id}/settings"),
            headers=headers,
            json=settings,
        )

        return self.process_response(response)

    def update_store_snaps(self, session, store_id, snaps):
        headers = self._get_authorization_header(session)

        response = self.session.post(
            url=self.get_endpoint_url(f"{store_id}/snaps"),
            headers=headers,
            json=snaps,
        )

        return self.process_response(response)

    def update_store_invites(self, session, store_id, invites):
        headers = self._get_authorization_header(session)

        response = self.session.put(
            url=self.get_endpoint_url(f"{store_id}/invites"),
            headers=headers,
            json=invites,
        )

        return self.process_response(response)

    def get_store_invites(self, session, store_id):
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url(f"{store_id}"),
            headers=headers,
        )

        return self.process_response(response).get("invites", [])
