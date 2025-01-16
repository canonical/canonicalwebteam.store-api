from os import getenv
from pprint import pprint
from requests import Session
from pymacaroons import Macaroon

from canonicalwebteam.store_api.base import Base
from canonicalwebteam.store_api.exceptions import (
    PublisherMacaroonRefreshRequired,
)


DASHBOARD_API_URL = getenv(
    "DASHBOARD_API_URL", "https://dashboard.snapcraft.io/"
)


class Dashboard(Base):
    def __init__(self, session: Session):
        super().__init__(session)

        self.config = {
            1: {"base_url": f"{DASHBOARD_API_URL}dev/api/"},
            2: {"base_url": f"{DASHBOARD_API_URL}api/v2/"},
        }

    def get_endpoint_url(self, endpoint, api_version=1, is_store=False):
        if is_store:
            base_url = self.config[api_version]["base_url"]
            return f"{base_url}stores/{endpoint}"
        base_url = self.config[api_version]["base_url"]
        return f"{base_url}{endpoint}"

    def _get_authorization_header(self, session):
        """
        Bind root and discharge macaroons and return the authorization header.
        """
        if "macaroon_root" in session:
            root = session["macaroon_root"]
            discharge = session["macaroon_discharge"]

            bound = (
                Macaroon.deserialize(root)
                .prepare_for_request(Macaroon.deserialize(discharge))
                .serialize()
            )

            return {
                "Authorization": f"macaroon root={root}, discharge={bound}"
            }
        # With Candid the header is Macaroons
        elif "macaroons" in session:
            return {"Macaroons": session["macaroons"]}

    def get_macaroon(self, permissions):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
        Documemntation:
            https://dashboard.snapcraft.io/docs/reference/v1/macaroon.html
        Endpoint: [POST] https://dashboard.snapcraft.io/dev/api/acl
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
            url=self.get_endpoint_url("tokens/whoami", api_version=2),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def get_account(self, session):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account
        Endpoint: [GET] https://dashboard.snapcraft.io/dev/api/account
        """
        headers = self._get_authorization_header(session)
        response = self.session.get(
            url=self.get_endpoint_url("account"), headers=headers
        )
        return self.process_response(response)

    def get_account_snaps(self, session):
        """
        Returns the snaps associated with a user account
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account
        Endpoint: [GET] https://dashboard.snapcraft.io/dev/api/account
        """
        pprint(self.get_account(session).get("snaps", {}).get("16", {}))
        return self.get_account(session).get("snaps", {}).get("16", {})

    def get_agreement(self, session):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#release-a-snap-build-to-a-channel
        Endpoint: [GET] https://dashboard.snapcraft.io/dev/api/agreement
        """
        headers = self._get_authorization_header(session)
        agreement_response = self.session.get(
            url=self.get_endpoint_url("agreement/"), headers=headers
        )

        if self._is_macaroon_expired(agreement_response.headers):
            raise PublisherMacaroonRefreshRequired

        return agreement_response.json()

    def post_agreement(self, session, agreed):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#release-a-snap-build-to-a-channel
        Endpoint: [POST] https://dashboard.snapcraft.io/dev/api/agreement
        """
        headers = self._get_authorization_header(session)

        json = {"latest_tos_accepted": agreed}
        agreement_response = self.session.post(
            url=self.get_endpoint_url("agreement/"), headers=headers, json=json
        )

        return self.process_response(agreement_response)

    def post_username(self, session, username):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account
        Endpoint: [PATCH] https://dashboard.snapcraft.io/dev/api/account
        """
        headers = self._get_authorization_header(session)
        json = {"short_namespace": username}
        username_response = self.session.patch(
            url=self.get_endpoint_url("account"), headers=headers, json=json
        )

        if username_response.status_code == 204:
            return {}
        else:
            return self.process_response(username_response)

    def post_register_name(
        self,
        session,
        snap_name,
        registrant_comment=None,
        is_private=False,
        store=None,
    ):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#register-a-snap-name
        Endpoint: [POST] https://dashboard.snapcraft.io/dev/api/register-name/
        """
        json = {"snap_name": snap_name}

        if registrant_comment:
            json["registrant_comment"] = registrant_comment

        if is_private:
            json["is_private"] = is_private

        if store:
            json["store"] = store

        response = self.session.post(
            url=self.get_endpoint_url("register-name/"),
            headers=self._get_authorization_header(session),
            json=json,
        )
        pprint(response.json())

        return self.process_response(response)

    def post_register_name_dispute(self, session, snap_name, claim_comment):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#register-a-snap-name-dispute
        Endpoint: [POST]
            https://dashboard.snapcraft.io/dev/api/register-name-dispute
        """
        json = {"snap_name": snap_name, "comment": claim_comment}

        response = self.session.post(
            url=self.get_endpoint_url("register-name-dispute/"),
            headers=self._get_authorization_header(session),
            json=json,
        )

        return self.process_response(response)

    def get_snap_info(self, snap_name, session):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#obtaining-information-about-a-snap
        Endpoint: [GET]
            https://dashboard.snapcraft.io/dev/api/snaps/info/{snap_name}
        """
        response = self.session.get(
            url=self.get_endpoint_url(f"snaps/info/{snap_name}"),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def get_package_upload_macaroon(self, session, snap_name, channels):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/macaroon.html#request-a-macaroon
        Endpoint: [POST] https://dashboard.snapcraft.io/dev/api/acl/
        """
        json = {
            "packages": [{"name": snap_name, "series": "16"}],
            "permissions": ["package_upload"],
            "channels": channels,
        }

        response = self.session.post(
            url=self.get_endpoint_url("acl/"),
            headers=self._get_authorization_header(session),
            json=json,
        )

        return self.process_response(response)

    def get_snap_id(self, snap_name, session):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#obtaining-information-about-a-snap
        Endpoint: https://dashboard.snapcraft.io/dev/api/snaps/info/{snap_name}
        """
        snap_info = self.get_snap_info(snap_name, session)

        return snap_info["snap_id"]

    def snap_metadata(self, snap_id, session, json=None):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#managing-snap-metadata
        Endpoint: [PUT]
            https://dashboard.snapcraft.io/dev/api/snaps/{snap_id}/metadata
        """
        method = "PUT" if json is not None else None

        metadata_response = self.session.request(
            method=method,
            url=self.get_endpoint_url(f"snaps/{snap_id}/metadata"),
            params={"conflict_on_update": "true"},
            headers=self._get_authorization_header(session),
            json=json,
        )

        return self.process_response(metadata_response)

    def snap_screenshots(self, snap_id, session, data=None, files=None):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#managing-snap-metadata
        Endpoint: [GET, PUT]
            https://dashboard.snapcraft.io/dev/api/snaps/{snap_id}/binary-metadata
        """
        method = "GET"
        files_array = None
        headers = self._get_authorization_header(session)
        headers["Accept"] = "application/json"

        if data:
            method = "PUT"

            files_array = []
            if files:
                for f in files:
                    files_array.append(
                        (f.filename, (f.filename, f.stream, f.mimetype))
                    )
            else:
                # API requires a multipart request, but we have no files to
                # push https://github.com/requests/requests/issues/1081
                files_array = {"info": ("", data["info"])}
                data = None

        screenshot_response = self.session.request(
            method=method,
            url=self.get_endpoint_url(f"snaps/{snap_id}/binary-metadata"),
            params={"conflict_on_update": "true"},
            headers=headers,
            data=data,
            files=files_array,
        )

        return self.process_response(screenshot_response)

    def get_snap_revision(self, session, snap_id, revision_id):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/macaroon.html#request-a-macaroon
        Endpoint: [GET]
            https://dashboard.snapcraft.io/api/v2/snaps/{snap_id}/revisions/{revision_id}
        """
        response = self.session.get(
            url=self.get_endpoint_url(
                f"snaps/{snap_id}/revisions/{revision_id}", api_version=2
            ),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def snap_release_history(self, session, snap_name, page=1):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/snaps.html#snap-releases
        Endpoint: [GET]
            https://dashboard.snapcraft.io/api/v2/snaps/{snap_name}/releases
        """
        response = self.session.get(
            url=self.get_endpoint_url(
                f"snaps/{snap_name}/releases", api_version=2
            ),
            params={"page": page},
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def snap_channel_map(self, session, snap_name):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/snaps.html#snap-channel-map
        Endpoint: [GET]
            https://dashboard.snapcraft.io/api/v2/snaps/{snap_name}/channel-map
        """
        response = self.session.get(
            url=self.get_endpoint_url(
                f"snaps/{snap_name}/channel-map", api_version=2
            ),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def post_snap_release(self, session, snap_name, json):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#release-a-snap-build-to-a-channel
        Endpoint: [POST] https://dashboard.snapcraft.io/dev/api/snap-release
        """
        response = self.session.post(
            url=self.get_endpoint_url("snap-release/"),
            headers=self._get_authorization_header(session),
            json=json,
        )

        return self.process_response(response)

    def post_close_channel(self, session, snap_id, json):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#close-a-channel-for-a-snap-package
        Endpoint: [POST]
            https://dashboard.snapcraft.io/dev/api/snaps/{snap_id}/close
        """
        response = self.session.post(
            url=self.get_endpoint_url(f"snaps/{snap_id}/close"),
            headers=self._get_authorization_header(session),
            json=json,
        )

        return self.process_response(response)

    def get_publisher_metrics(self, session, json):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#fetch-metrics-for-snaps
        Endpoint: [POST] https://dashboard.snapcraft.io/dev/api/snaps/metrics
        """
        headers = self._get_authorization_header(session)
        headers["Content-Type"] = "application/json"

        metrics_response = self.session.post(
            url=self.get_endpoint_url("snaps/metrics"),
            headers=headers,
            json=json,
        )

        return self.process_response(metrics_response)

    def get_validation_sets(self, publisher_auth):
        """
        Return a list of validation sets for the current account
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/validation-sets.html
        Endpoint: [GET] https://dashboard.snapcraft.io/api/v2/validation-sets
        """
        url = self.get_endpoint_url("validation-sets", api_version=2)
        response = self.session.get(
            url, headers=self._get_authorization_header(publisher_auth)
        )
        return self.process_response(response)

    def get_validation_set(self, publisher_auth, validation_set_id):
        """
        Return a validation set for the current account
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v2/en/validation-sets.html
        Endpoint:
            [GET] https://dashboard.snapcraft.io/api/v2/validation-sets/{id}
        """
        url = self.get_endpoint_url(
            f"validation-sets/{validation_set_id}?sequence=all", api_version=2
        )
        response = self.session.get(
            url, headers=self._get_authorization_header(publisher_auth)
        )
        return self.process_response(response)

    def get_stores(self, session, roles=["admin", "review", "view", "access"]):
        """Return a list a stores with the given roles
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/account.html#get--dev-api-account
        Endpoint: [GET] https://dashboard.snapcraft.io/dev/api/account

        :return: A list of stores
        """
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url("account", 1), headers=headers
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
            url=self.get_endpoint_url(store_id, api_version=2, is_store=True),
            headers=headers,
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
            url=self.get_endpoint_url(
                f"{store_id}/snaps", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}/users", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}/invites", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}/settings", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}/snaps", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}/invites", api_version=2, is_store=True
            ),
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
            url=self.get_endpoint_url(
                f"{store_id}", api_version=2, is_store=True
            ),
            headers=headers,
        )
        return self.process_response(response).get("invites", [])
