from os import getenv

import requests

from canonicalwebteam.store_api.store import Store

SNAPSTORE_API_URL = getenv("CHARMSTORE_API_URL", "https://api.snapcraft.io/")


class CharmStore(Store):
    def __init__(self, session=requests.Session(), store=None):
        super().__init__(session, store)

        self.config = {
            2: {"base_url": f"{SNAPSTORE_API_URL}v2/charms/"},
        }
