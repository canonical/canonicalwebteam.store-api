from os import getenv

import requests

from canonicalwebteam.store_api.store import Store
from canonicalwebteam.store_api.publisher import Publisher

SNAPSTORE_API_URL = getenv("SNAPSTORE_API_URL", "https://api.snapcraft.io/")
SNAPSTORE_DASHBOARD_API_URL = getenv(
    "SNAPSTORE_DASHBOARD_API_URL", "https://dashboard.snapcraft.io/"
)
SNAPSTORE_PUBLISHERWG_API_URL = getenv(
    "SNAPSTORE_PUBLISHERWG_API_URL", "https://api.charmhub.io/"
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
            "media",
            "download",
            "version",
            "created-at",
            "confinement",
            "categories",
            "trending",
            "unlisted",
            "links",
        ],
        api_version=1,
    ):
        return super(SnapStore, self).get_item_details(
            name, None, fields, api_version
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
        Documemntation:
            https://dashboard.snapcraft.io/docs/reference/v1/macaroon.html
        Endpoint: [POST] https://dashboard.snapcraft.iodev/api/acl
        """
        response = self.session.post(
            url=self.get_endpoint_url("tokens", 2),
            json={"permissions": permissions},
        )

        return self.process_response(response)["macaroon"]

    def whoami(self, session):
        """
        Get the authenticated user details.
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/tokens.html#api-tokens-whoami
        Endpoint: [GET] https://dashboard.snapcraft.io/api/v2/tokens/whoami
        """
        response = self.session.get(
            url=self.get_endpoint_url("tokens/whoami", 2),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def get_publisherwg_endpoint_url(self, endpoint):
        return f"{SNAPSTORE_PUBLISHERWG_API_URL}v1/{endpoint}"

    def _get_publisherwg_authorization_header(self, session):
        return {"Authorization": f"Macaroon {session['developer_token']}"}

    def exchange_dashboard_macaroons(self, session):
        """
        Exchange dashboard.snapcraft.io SSO discharged macaroons
        Documentation:
            https://api.charmhub.io/docs/default.html#exchange_dashboard_macaroons
        Endpoint: [POST] https://api.charmhub.io/v1/tokens/dashboard/exchange
        """
        response = self.session.post(
            url=self.get_publisherwg_endpoint_url("tokens/dashboard/exchange"),
            headers=self._get_authorization_header(session),
            json={},
        )

        return self.process_response(response)["macaroon"]

    def get_collaborators(self, session, name):
        """
        Get collaborators (accepted invites) for the given package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#get_collaborators
        Endpoint: [GET]
            https://api.charmhub.io/v1/snap/{snap_name}/collaborators
        """
        response = self.session.get(
            url=self.get_publisherwg_endpoint_url(
                f"snap/{name}/collaborators"
            ),
            headers=self._get_publisherwg_authorization_header(session),
        )
        return self.process_response(response)

    def get_pending_invites(self, session, name):
        """
        Get pending collaborator invites for the given package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#get_pending_invites
        Endpoint: [GET]
            https://api.charmhub.io/v1/snap/{snap_name}/collaborators/invites
        """
        response = self.session.get(
            url=self.get_publisherwg_endpoint_url(
                f"snap/{name}/collaborators/invites"
            ),
            headers=self._get_publisherwg_authorization_header(session),
        )
        return self.process_response(response)

    def invite_collaborators(self, session, name, emails):
        """
        Invite one or more collaborators for a package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#invite_collaborators
        Endpoint: [POST]
            https://api.charmhub.io/v1/snap/{snap_name}/collaborators/invites
        """
        payload = {"invites": []}

        for email in emails:
            payload["invites"].append({"email": email})

        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(
                f"snap/{name}/collaborators/invites"
            ),
            headers=self._get_publisherwg_authorization_header(session),
            json=payload,
        )
        return self.process_response(response)

    def revoke_invites(self, session, name, emails):
        """
        Revoke invites to the specified emails for the package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#revoke_invites
        Endpoint: [POST]
            https://api.charmhub.io/v1/snap/{snap_name}/collaborators/invites/revoke
        """
        payload = {"invites": []}

        for email in emails:
            payload["invites"].append({"email": email})

        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(
                f"snap/{name}/collaborators/invites/revoke"
            ),
            headers=self._get_publisherwg_authorization_header(session),
            json=payload,
        )
        return self.process_response(response)

    def accept_invite(self, session, name, token):
        """
        Accept a collaborator invite.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#accept_invite
        Endpoint: [POST]
            https://api.charmhub.io/v1/snap/{snap_name}/collaborators/invites/accept
        """
        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(
                f"snap/{name}/collaborators/invites/accept"
            ),
            headers=self._get_publisherwg_authorization_header(session),
            json={"token": token},
        )
        return self.process_response(response)

    def reject_invite(self, session, name, token):
        """
        Reject a collaborator invite.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#reject_invite
        Endpoint: [POST]
            https://api.charmhub.io/v1/snap/{snap_name}/collaborators/invites/reject
        """
        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(
                f"snap/{name}/collaborators/invites/reject"
            ),
            headers=self._get_publisherwg_authorization_header(session),
            json={"token": token},
        )
        return self.process_response(response)

    def create_track(self, session, snap_name, track_name):
        """
        Create a track for a snap base on the snap's guardrail pattern.
        Documentation: https://api.charmhub.io/docs/default.html#create_tracks
        Endpoint: [POST]  https://api.charmhub.io/v1/snap/{snap_name}/tracks
        """
        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(f"snap/{snap_name}/tracks"),
            headers=self._get_publisherwg_authorization_header(session),
            json=[{"name": track_name}],
        )
        return response

    def unregister_package_name(self, publisher_auth, snap_name):
        """
        Unregister a package name.
        Documentation: https://api.charmhub.io/docs/default.html#register_name
        Endpoint: [DELETE] https://api.charmhub.io/v1/snap/{snap_name}

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package to unregister
        Returns:
            The package name ID if successful
            Otherwise, returns an error list
        """
        url = self.get_publisherwg_endpoint_url(f"snap/{snap_name}")
        response = self.session.delete(
            url=url,
            headers=self._get_authorization_header(publisher_auth),
        )
        return response


class SnapStoreAdmin(SnapPublisher):
    def get_endpoint_url(self, endpoint, api_version=2):
        return super().get_endpoint_url(f"stores/{endpoint}", api_version)

    def get_stores(self, session, roles=["admin", "review", "view", "access"]):
        """Return a list a stores with the given roles
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account
        Endpoint: [GET] https://dashboard.snapcraft.io/dev/api/account

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
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#list-the-details-of-a-brand-store
        Endpoint:  [GET]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}

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
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#get
        Endpoint: [GET]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}/snaps
        """
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
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#list-the-details-of-a-brand-store
        Endpoint: [GET] https://dashboard.snapcraft.io/api/v2/stores/{store_id}
        """
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url(f"{store_id}"),
            headers=headers,
        )

        return self.process_response(response).get("users", [])

    def update_store_members(self, session, store_id, members):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#add-remove-or-edit-users-roles
        Endpoint: [POST]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}/users
        """
        headers = self._get_authorization_header(session)

        response = self.session.post(
            url=self.get_endpoint_url(f"{store_id}/users"),
            headers=headers,
            json=members,
        )

        return self.process_response(response)

    def invite_store_members(self, session, store_id, members):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#manage-store-invitations
        Endpoint: [POST]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}/invites
        """
        headers = self._get_authorization_header(session)

        response = self.session.post(
            url=self.get_endpoint_url(f"{store_id}/invites"),
            headers=headers,
            json=members,
        )

        return self.process_response(response)

    def change_store_settings(self, session, store_id, settings):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#change-store-settings
        Endpoint: [PUT]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}/settings
        """
        headers = self._get_authorization_header(session)

        response = self.session.put(
            url=self.get_endpoint_url(f"{store_id}/settings"),
            headers=headers,
            json=settings,
        )

        return self.process_response(response)

    def update_store_snaps(self, session, store_id, snaps):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#post
        Endpoint: [POST]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}/snaps
        """
        headers = self._get_authorization_header(session)

        response = self.session.post(
            url=self.get_endpoint_url(f"{store_id}/snaps"),
            headers=headers,
            json=snaps,
        )

        return self.process_response(response)

    def update_store_invites(self, session, store_id, invites):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#manage-store-invitations
        Endpoint: [PUT]
            https://dashboard.snapcraft.io/api/v2/stores/{store_id}/invites
        """
        headers = self._get_authorization_header(session)

        response = self.session.put(
            url=self.get_endpoint_url(f"{store_id}/invites"),
            headers=headers,
            json=invites,
        )

        return self.process_response(response)

    def get_store_invites(self, session, store_id):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/stores.html#list-the-details-of-a-brand-store
        Endpoint: [GET] https://dashboard.snapcraft.io/api/v2/stores/{store_id}
        """
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url(f"{store_id}"),
            headers=headers,
        )

        return self.process_response(response).get("invites", [])

    # MODEL SERVICE ADMIN
    def get_store_models(self, session, store_id):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#read_models
        Endpoint: [GET] https://api.charmhub.io/v1/brand/{store_id}/model
        """
        response = self.session.get(
            url=self.get_publisherwg_endpoint_url(f"brand/{store_id}/model"),
            headers=self._get_publisherwg_authorization_header(session),
        )

        return self.process_response(response)

    def create_store_model(self, session, store_id, name, api_key=None):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#create_model
        Endpoint: [POST] https://api.charmhub.io/v1/brand/{store_id}/model
        """
        if api_key:
            payload = {"name": name, "api-key": api_key, "series": "16"}
        else:
            payload = {"name": name, "series": "16"}
        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(f"brand/{store_id}/model"),
            headers=self._get_publisherwg_authorization_header(session),
            json=payload,
        )

        return self.process_response(response)

    def update_store_model(self, session, store_id, model_name, api_key):
        """
        Doucumentation:
            https://api.charmhub.io/docs/model-service-admin.html#update_model
        Endpoint: [PATCH]
            https://api.charmhub.io/v1/brand/{store_id}/model/{model_name}
        """
        response = self.session.patch(
            url=self.get_publisherwg_endpoint_url(
                f"brand/{store_id}/model/{model_name}"
            ),
            headers=self._get_publisherwg_authorization_header(session),
            json={"api-key": api_key},
        )

        return self.process_response(response)

    def get_store_model_policies(self, session, store_id, model_name):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#read_serial_policies
        Endpoint: [GET]
            https://api.charmhub.io/v1/brand/{store_id}/model/<model_name>/serial_policy
        """
        response = self.session.get(
            url=self.get_publisherwg_endpoint_url(
                f"brand/{store_id}/model/{model_name}/serial_policy"
            ),
            headers=self._get_publisherwg_authorization_header(session),
        )

        return self.process_response(response)

    def create_store_model_policy(
        self, session, store_id, model_name, signing_key
    ):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#create_serial_policy
        Endpoint: [POST]
            https://api.charmhub.io/v1/brand/{store_id}/model/{model_name}/serial_policy
        """
        response = self.session.post(
            url=self.get_publisherwg_endpoint_url(
                f"brand/{store_id}/model/{model_name}/serial_policy"
            ),
            headers=self._get_publisherwg_authorization_header(session),
            json={"signing-key-sha3-384": signing_key},
        )

        return self.process_response(response)

    def delete_store_model_policy(
        self, session, store_id, model_name, revision
    ):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#delete_serial_policy
        Endpoint: [DELETE]
            https://api.charmhub.io/v1/brand/{store_id}/model/{model_name}/serial_policy/{serial_policy_revision}
        """
        response = self.session.delete(
            url=self.get_publisherwg_endpoint_url(
                f"brand/{store_id}/model/{model_name}/serial_policy/{revision}"
            ),
            headers=self._get_publisherwg_authorization_header(session),
        )

        return response

    def get_store_signing_keys(self, session, store_id):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#read_signing_keys
        Endpoint: [GET] https://api.charmhub.io/v1/brand/{store_id}/signing_key
        """
        headers = self._get_publisherwg_authorization_header(session)
        url = self.get_publisherwg_endpoint_url(
            f"brand/{store_id}/signing_key"
        )
        response = self.session.get(
            url=url,
            headers=headers,
        )
        return self.process_response(response)

    def create_store_signing_key(self, session, store_id, name):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#create_signing_key
        Endpoint: [POST]
            https://api.charmhub.io/v1/brand/{store_id}/signing_key
        """
        headers = self._get_publisherwg_authorization_header(session)
        url = self.get_publisherwg_endpoint_url(
            f"brand/{store_id}/signing_key"
        )
        response = self.session.post(
            url=url,
            headers=headers,
            json={"name": name},
        )
        return self.process_response(response)

    def delete_store_signing_key(
        self, session, store_id, signing_key_sha3_384
    ):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#delete_signing_key
        Endpoint: [DELETE]
            https://api.charmhub.io/v1/brand/{store_id}/signing_key/<signing_key_sha3_384}
        """
        headers = self._get_publisherwg_authorization_header(session)
        url = self.get_publisherwg_endpoint_url(
            f"brand/{store_id}/signing_key/{signing_key_sha3_384}"
        )
        response = self.session.delete(
            url=url,
            headers=headers,
        )

        return response

    def get_brand(self, session, store_id):
        """
        Documentation:
            https://api.charmhub.io/docs/model-service-admin.html#read_brand
        Endpoint: [GET] https://api.charmhub.io/v1/brand/{store_id}
        """
        headers = self._get_publisherwg_authorization_header(session)
        url = self.get_publisherwg_endpoint_url(f"brand/{store_id}")
        response = self.session.get(
            url=url,
            headers=headers,
        )

        return self.process_response(response)

    # FEATURED SNAPS AUTOMATION
    def delete_featured_snaps(self, session, snaps):
        """
        Documentation: (link to spec)
            https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8
        Endpoint: [DELETE] https://api.charmhub.io/v1/snap/featured
        """
        headers = self._get_publisherwg_authorization_header(session)
        url = self.get_publisherwg_endpoint_url("snap/featured")
        response = self.session.delete(
            url=url,
            headers=headers,
            json=snaps,
        )
        return response

    def update_featured_snaps(self, session, snaps):
        """
        Documentation: (link to spec)
            https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8
        Endpoint: [PUT] https://api.charmhub.io/v1/snap/featured
        """
        headers = self._get_publisherwg_authorization_header(session)
        url = self.get_publisherwg_endpoint_url("snap/featured")
        response = self.session.put(
            url=url,
            headers=headers,
            json=snaps,
        )
        return response

    def get_featured_snaps(self, session, api_version=1, fields="snap_id"):
        """
        Documentation: (link to spec)
            https://docs.google.com/document/d/1UAybxuZyErh3ayqb4nzL3T4BbvMtnmKKEPu-ixcCj_8/edit
        Endpoint: https://api.snapcraft.io/api/v1/snaps/search
        """
        url = f"{SNAPSTORE_API_URL}api/v1/snaps/search"
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
