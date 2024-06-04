from canonicalwebteam.store_api.exceptions import (
    StoreApiConnectionError,
    StoreApiResourceNotFound,
    StoreApiResponseDecodeError,
    StoreApiResponseError,
    StoreApiResponseErrorList,
    PublisherAgreementNotSigned,
    PublisherMacaroonRefreshRequired,
    PublisherMissingUsername,
)
from pymacaroons import Macaroon


class Publisher:
    def __init__(self, session):
        self.config = {1: {"base_url": ""}}
        self.session = session

    def process_response(self, response):
        # 5xx responses are not in JSON format
        if response.status_code >= 500:
            raise StoreApiConnectionError("Service Unavailable")

        try:
            body = response.json()
        except ValueError as decode_error:
            api_error_exception = StoreApiResponseDecodeError(
                "JSON decoding failed: {}".format(decode_error)
            )
            raise api_error_exception

        if self._is_macaroon_expired(response.headers):
            raise PublisherMacaroonRefreshRequired

        if not response.ok:
            error_list = (
                body["error_list"]
                if "error_list" in body
                else body.get("error-list")
            )
            if "error_list" in body or "error-list" in body:
                for error in error_list:
                    if error["code"] == "user-missing-latest-tos":
                        raise PublisherAgreementNotSigned
                    if error["code"] == "user-not-ready":
                        if "has not signed agreement" in error["message"]:
                            raise PublisherAgreementNotSigned
                        elif "username" in error["message"]:
                            raise PublisherMissingUsername
                    if error["code"] == "resource-not-found":
                        raise StoreApiResourceNotFound

                raise StoreApiResponseErrorList(
                    "The api returned a list of errors",
                    response.status_code,
                    error_list,
                )
            elif not body:
                raise StoreApiResponseError(
                    "Unknown error from api", response.status_code
                )

        return body

    def get_endpoint_url(self, endpoint, api_version=1):
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

    def _is_macaroon_expired(self, headers):
        """
        Returns True if the macaroon needs to be refreshed from
        the header response.
        """
        return headers.get("WWW-Authenticate") == ("Macaroon needs_refresh=1")

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
                f"snaps/{snap_id}/revisions/{revision_id}", 2
            ),
            headers=self._get_authorization_header(session),
        )

        return self.process_response(response)

    def snap_revision_history(self, session, snap_id):
        """
        Documentation:
            https://dashboard.snapcraft.io/docs/reference/v1/snap.html#list-all-revisions-of-a-snap
        Endpoint: [GET]
            https://dashboard.snapcraft.io/dev/api/snaps/{snap_id}/history
        """
        response = self.session.get(
            url=self.get_endpoint_url(f"snaps/{snap_id}/history"),
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
            url=self.get_endpoint_url(f"snaps/{snap_name}/releases", 2),
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
            url=self.get_endpoint_url(f"snaps/{snap_name}/channel-map", 2),
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
