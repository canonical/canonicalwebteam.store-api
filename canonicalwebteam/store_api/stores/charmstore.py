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


class CharmPublisher(Publisher):
    def __init__(self, session=requests.Session()):
        super().__init__(session)

        self.config = {
            1: {"base_url": f"{CHARMSTORE_PUBLISHER_API_URL}v1/"},
        }

        self.session.headers.update({"Bakery-Protocol-Version": "2"})

    def _get_authorization_header(self, publisher_auth):
        return {"Authorization": f"Macaroon {publisher_auth}"}

    def get_macaroon(self):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
        """
        response = self.session.get(url=self.get_endpoint_url("tokens"))

        return self.process_response(response)["macaroon"]

    def issue_macaroon(self, permissions, description=None, ttl=None):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
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
        """
        response = self.session.get(
            url=self.get_endpoint_url("tokens/whoami"),
            headers=self._get_authorization_header(publisher_auth),
        )

        return self.process_response(response)

    def whoami(self, publisher_auth):
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

    def get_charm_libraries(self, charm_name):
        response = self.session.post(
            url=self.get_endpoint_url("charm/libraries/bulk"),
            json=[{"charm-name": charm_name}],
        )

        return self.process_response(response)

    def get_charm_library(self, charm_name, library_id, api_version=None):
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
