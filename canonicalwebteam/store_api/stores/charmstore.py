from os import getenv

import requests

from canonicalwebteam.store_api.store import Store
from canonicalwebteam.store_api.publisher import Publisher

CHARMSTORE_API_URL = getenv("CHARMSTORE_API_URL", "https://api.snapcraft.io/")
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
        return {"Macaroons": publisher_auth}

    def get_macaroon(self):
        """
        Return a bakery v2 macaroon from the publisher API to be discharged
        """
        response = self.session.get(url=self.get_endpoint_url("tokens"))

        return self.process_response(response)["macaroon"]

    def whoami(self, publisher_auth):
        response = self.session.get(
            url=self.get_endpoint_url("whoami"),
            headers=self._get_authorization_header(publisher_auth),
        )

        return self.process_response(response)

    def get_account_packages(self, publisher_auth, package_type, status=None):
        """
        Return publisher packages

        Args:
            publisher_auth: Serialized macaroon to consume the API.
            package_type: Type of packages to obtain.
            status (optional): Only packages with the given status

        Returns:
            A list of packages
        """

        if package_type not in CHARMSTORE_VALID_PACKAGE_TYPES:
            raise ValueError(
                "Invalid package type. Expected one of: %s"
                % CHARMSTORE_VALID_PACKAGE_TYPES
            )

        response = self.session.get(
            url=self.get_endpoint_url(package_type),
            headers=self._get_authorization_header(publisher_auth),
        )
        packages = self.process_response(response)["results"]

        if status:
            packages = [p for p in packages if p["status"] == status]

        return packages
