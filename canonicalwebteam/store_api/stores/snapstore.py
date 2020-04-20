from os import getenv

import requests

from canonicalwebteam.store_api.store import Store

SNAPSTORE_API_URL = getenv("SNAPSTORE_API_URL", "https://api.snapcraft.io/")


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
            "architecture",
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
            name, fields, api_version
        )
