from canonicalwebteam.exceptions import (
    StoreApiConnectionError,
    StoreApiResourceNotFound,
    StoreApiResponseDecodeError,
    StoreApiResponseError,
    StoreApiResponseErrorList,
    PublisherAgreementNotSigned,
    PublisherMacaroonRefreshRequired,
    PublisherMissingUsername,
)


class Base:
    def __init__(self, session):
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

    def _is_macaroon_expired(self, headers):
        """
        Returns True if the macaroon needs to be refreshed from
        the header response.
        """
        return headers.get("WWW-Authenticate") == ("Macaroon needs_refresh=1")
