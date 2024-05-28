from os import getenv

import requests

from canonicalwebteam.store_api.store import Store
from canonicalwebteam.store_api.publisher import Publisher

CHARMSTORE_API_URL = getenv("CHARMSTORE_API_URL", "https://api.charmhub.io/")
CHARMSTORE_PUBLISHER_API_URL = getenv(
    "CHARMSTORE_PUBLISHER_API_URL", "https://api.charmhub.io/"
)
CHARMSTORE_VALID_PACKAGE_TYPES = ["charm", "bundle"]


class CharmStore(Store):
    def __init__(self, session=requests.Session(), store=None):
        super().__init__(session, store)

        self.config = {
            2: {"base_url": f"{CHARMSTORE_API_URL}v2/charms/"},
        }

    def find(
        self,
        query="",
        category="",
        publisher="",
        type=None,
        provides=[],
        requires=[],
        fields=[],
    ):
        """
        Given a search term, return an array of matching search results.
        v2 API only.
        """
        url = self.get_endpoint_url("find", 2)
        headers = self.config[2].get("headers")
        params = {
            "q": query,
            "category": category,
            "publisher": publisher,
            "type": type,
        }
        if fields:
            params["fields"] = ",".join(fields)

        if provides:
            params["provides"] = ",".join(provides)

        if requires:
            params["requires"] = ",".join(requires)

        return self.process_response(
            self.session.get(url, params=params, headers=headers)
        )


class CharmPublisher(Publisher):
    def __init__(self, session=requests.Session()):
        super().__init__(session)

        self.config = {
            1: {"base_url": f"{CHARMSTORE_PUBLISHER_API_URL}v1/"},
        }

        self.session.headers.update({"Bakery-Protocol-Version": "2"})

    def _get_authorization_header(self, publisher_auth):
        """
        Return the formatted Authorization header for the publisher API.
        """
        return {"Authorization": f"Macaroon {publisher_auth}"}

    def get_macaroon(self):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
        Documentation: https://api.charmhub.io/docs/default.html#get_macaroon
        Endpoint URL: [GET] https://api.charmhub.io/v1/tokens
        """
        response = self.session.get(url=self.get_endpoint_url("tokens"))

        return self.process_response(response)["macaroon"]

    def issue_macaroon(self, permissions, description=None, ttl=None):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
        Documentation: https://api.charmhub.io/docs/default.html#issue_macaroon
        Endpoint URL: [POST] https://api.charmhub.io/v1/tokens
        """
        data = {"permissions": permissions}

        if description:
            data["description"] = description

        if ttl:
            data["ttl"] = ttl

        response = self.session.post(
            url=self.get_endpoint_url("tokens"),
            json=data,
        )

        return self.process_response(response)["macaroon"]

    def exchange_macaroons(self, issued_macaroon):
        """
        Return an exchanged snapstore-only authentication macaroon.
        Documentation:
            https://api.charmhub.io/docs/default.html#exchange_macaroons
        Endpoint URL: [POST] https://api.charmhub.io/v1/tokens/exchange
        """

        response = self.session.post(
            url=self.get_endpoint_url("tokens/exchange"),
            headers={"Macaroons": issued_macaroon},
            json={},
        )

        return self.process_response(response)["macaroon"]

    def macaroon_info(self, publisher_auth):
        """
        Return information about the authenticated macaroon token.
        Documentation: https://api.charmhub.io/docs/default.html#macaroon_info
        Endpoint URL: [GET] https://api.charmhub.io/v1/tokens/whoami
        """
        response = self.session.get(
            url=self.get_endpoint_url("tokens/whoami"),
            headers=self._get_authorization_header(publisher_auth),
        )

        return self.process_response(response)

    def whoami(self, publisher_auth):
        """
        Return information about the authenticated macaroon token.
        Documentation: 'DEPRECATED'
        Endpoint URL: [GET] https://api.charmhub.io/v1/whoami
        """
        response = self.session.get(
            url=self.get_endpoint_url("whoami"),
            headers=self._get_authorization_header(publisher_auth),
        )

        return self.process_response(response)

    def get_account_packages(
        self,
        publisher_auth,
        package_type,
        include_collaborations=False,
        status=None,
    ):
        """
        Return publisher packages
        Documentation: https://api.charmhub.io/docs/default.html
        Endpoint URL: [GET] https://api.charmhub.io/v1/charm

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            package_type: Type of packages to obtain.
            include_collaborations (optional): Include shared charms
            status (optional): Only packages with the given status

        Returns:
            A list of packages
        """

        if package_type not in CHARMSTORE_VALID_PACKAGE_TYPES:
            raise ValueError(
                "Invalid package type. Expected one of: %s"
                % CHARMSTORE_VALID_PACKAGE_TYPES
            )

        params = {}

        if include_collaborations:
            params["include-collaborations"] = "true"

        response = self.session.get(
            url=self.get_endpoint_url(package_type),
            headers=self._get_authorization_header(publisher_auth),
            params=params,
        )
        packages = self.process_response(response)["results"]

        if status:
            packages = [p for p in packages if p["status"] == status]

        return packages

    def get_package_metadata(self, publisher_auth, package_type, name):
        """
        Get general metadata for a package.
        Documentation:
            https://api.charmhub.io/docs/default.html#package_metadata
        Endpoint URL: [GET] https://api.charmhub.io/v1/charm/<name>
        namespace: charm for both charms and bundles
        name: Package name

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            package_type: Type of packages to obtain.

        Returns:
            Package general metadata
        """

        if package_type not in CHARMSTORE_VALID_PACKAGE_TYPES:
            raise ValueError(
                "Invalid package type. Expected one of: %s"
                % CHARMSTORE_VALID_PACKAGE_TYPES
            )

        response = self.session.get(
            url=self.get_endpoint_url(f"{package_type}/{name}"),
            headers=self._get_authorization_header(publisher_auth),
        )

        return self.process_response(response)["metadata"]

    def update_package_metadata(
        self, publisher_auth, package_type, name, data
    ):
        """
        Update general metadata for a package.
        Documentation:
            https://api.charmhub.io/docs/default.html#update_package_metadata
        Endpoint URL: [PATCH]
            https://api.charmhub.io/v1/charm/<name>
        namespace: charm for both charms and bundles
        name: Package name

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            package_type: Type of packages to obtain.
            name: Package name
            data: Dict with changes to apply

        Returns:
            Package general metadata with changes applied
        """

        if package_type not in CHARMSTORE_VALID_PACKAGE_TYPES:
            raise ValueError(
                "Invalid package type. Expected one of: %s"
                % CHARMSTORE_VALID_PACKAGE_TYPES
            )

        response = self.session.patch(
            url=self.get_endpoint_url(f"{package_type}/{name}"),
            headers=self._get_authorization_header(publisher_auth),
            json=data,
        )

        return self.process_response(response)["metadata"]

    def register_package_name(self, publisher_auth, data):
        """
        Register a package name.
        Documentation: https://api.charmhub.io/docs/default.html#register_name
        Endpoint URL: [POST] https://api.charmhub.io/v1/charm

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            data: Dict with name, type and visibility of the package

        Returns:
            Newly registered name id
        """

        response = self.session.post(
            url=self.get_endpoint_url("charm"),
            headers=self._get_authorization_header(publisher_auth),
            json=data,
        )

        return self.process_response(response)

    def unregister_package_name(self, publisher_auth, name):
        """
        Unregister a package name.
        Documentation:
            https://api.charmhub.io/docs/default.html#unregister_package
        Endpoint URL: [DELETE] https://api.charmhub.io/v1/charm/<name>

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package to unregister
        Returns:
            The package name ID if successful
            Otherwise, returns an error list
        """
        url = self.get_endpoint_url(f"charm/{name}")
        response = self.session.delete(
            url=url,
            headers=self._get_authorization_header(publisher_auth),
        )
        return response

    def get_charm_libraries(self, charm_name):
        """
        Get libraries for a charm.
        Documentation:
            https://api.charmhub.io/docs/libraries.html#fetch_libraries
        Endpoint URL: [POST] https://api.charmhub.io/v1/charm/libraries/bulk
        """
        response = self.session.post(
            url=self.get_endpoint_url("charm/libraries/bulk"),
            json=[{"charm-name": charm_name}],
        )

        return self.process_response(response)

    def get_charm_library(self, charm_name, library_id, api_version=None):
        """
        Get library metadata and content
        Documentation:
            https://api.charmhub.io/docs/libraries.html#fetch_library
        Endpoint URL: [GET]
        https://api.charmhub.io/v1/charm/libraries/<charm_name>/<library_id>

        Args:
            charm_name: Name of the charm
            library_id: ID of the library
            api_version: API version to use
        """
        params = {}

        if api_version is not None:
            params["api"] = api_version

        response = self.session.get(
            url=self.get_endpoint_url(
                f"charm/libraries/{charm_name}/{library_id}"
            ),
            params=params,
        )

        return self.process_response(response)

    def get_collaborators(self, publisher_auth, name):
        """
        Get collaborators (accepted invites) for the given package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#get_collaborators
        Endpoint URL: [GET]
            https://api.charmhub.io/v1/charm/<name>/collaborators

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package
        """
        response = self.session.get(
            url=self.get_endpoint_url(f"charm/{name}/collaborators"),
            headers=self._get_authorization_header(publisher_auth),
        )
        return self.process_response(response)

    def get_pending_invites(self, publisher_auth, name):
        """
        Get pending collaborator invites for the given package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#get_pending_invites
        Endpoint URL: [GET]
            https://api.charmhub.io/v1/charm/<name>/collaborators/invites

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package
        """
        response = self.session.get(
            url=self.get_endpoint_url(f"charm/{name}/collaborators/invites"),
            headers=self._get_authorization_header(publisher_auth),
        )
        return self.process_response(response)

    def invite_collaborators(self, publisher_auth, name, emails):
        """
        Invite one or more collaborators for a package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#invite_collaborators
        Endpoint URL: [POST]
            https://api.charmhub.io/v1/charm/<name>/collaborators/invites

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package
            emails: List of emails to invite
        """
        payload = {"invites": []}

        for email in emails:
            payload["invites"].append({"email": email})

        response = self.session.post(
            url=self.get_endpoint_url(f"charm/{name}/collaborators/invites"),
            headers=self._get_authorization_header(publisher_auth),
            json=payload,
        )
        return self.process_response(response)

    def revoke_invites(self, publisher_auth, name, emails):
        """
        Revoke invites to the specified emails for the package.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#revoke_invites
        Endpoint URL: [POST]
            https://api.charmhub.io/v1/charm/<name>/collaborators/invites/revoke

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package
            emails: List of emails to revoke
        """
        payload = {"invites": []}

        for email in emails:
            payload["invites"].append({"email": email})

        response = self.session.post(
            url=self.get_endpoint_url(
                f"charm/{name}/collaborators/invites/revoke"
            ),
            headers=self._get_authorization_header(publisher_auth),
            json=payload,
        )
        return response

    def accept_invite(self, publisher_auth, name, token):
        """
        Accept a collaborator invite.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#accept_invite
        Endpoint URL: [POST]
            https://api.charmhub.io/v1/charm/<name>/collaborators/invites/accept

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package
            token: Invite token
        """
        response = self.session.post(
            url=self.get_endpoint_url(
                f"charm/{name}/collaborators/invites/accept"
            ),
            headers=self._get_authorization_header(publisher_auth),
            json={"token": token},
        )
        return response

    def reject_invite(self, publisher_auth, name, token):
        """
        Reject a collaborator invite.
        Documentation:
            https://api.charmhub.io/docs/collaborator.html#reject_invite
        Endpoint URL: [POST]
            https://api.charmhub.io/v1/charm/<name>/collaborators/invites/reject

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            name: Name of the package
            token: Invite token
        """
        response = self.session.post(
            url=self.get_endpoint_url(
                f"charm/{name}/collaborators/invites/reject"
            ),
            headers=self._get_authorization_header(publisher_auth),
            json={"token": token},
        )
        return response

    def create_track(self, publisher_auth, charm_name, track_name):
        """
        Create a track for a charm base on the charm's guardrail pattern.
        Documentation: https://api.charmhub.io/docs/default.html#create_tracks
        Endpoint URL: [POST]
            https://api.charmhub.io/v1/charm/<charm_name>/tracks

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            charm_name: Name of the charm
            track_name: Name of the track
        """
        response = self.session.post(
            url=self.get_endpoint_url(f"charm/{charm_name}/tracks"),
            headers=self._get_authorization_header(publisher_auth),
            json=[{"name": track_name}],
        )
        return response
