from os import getenv

import requests

from canonicalwebteam.store_api.store import Store
from canonicalwebteam.store_api.publisher import Publisher

CHARMSTORE_API_URL = getenv("CHARMSTORE_API_URL", "https://api.snapcraft.io/")
CHARMSTORE_PUBLISHER_API_URL = getenv(
    "CHARMSTORE_PUBLISHER_API_URL", "https://api.snapcraft.io/"
)


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
            1: {
                "base_url": f"{CHARMSTORE_PUBLISHER_API_URL}publisher/api/v1/"
            },
        }

    def _get_authorization_header(self, session):
        return {"Cookie": session["publisher-macaroon"]}

    def whoami(self, session):
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url("whoami"), headers=headers
        )

        return self.process_response(response)

    def get_account_packages(self, session):
        headers = self._get_authorization_header(session)

        response = self.session.get(
            url=self.get_endpoint_url("charm"), headers=headers
        )

        return self.process_response(response)
