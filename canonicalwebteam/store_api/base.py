import logging

from canonicalwebteam.exceptions import (
    PublisherAgreementNotSigned,
    PublisherMacaroonRefreshRequired,
    PublisherMissingUsername,
    StoreApiBadGatewayError,
    StoreApiConnectionError,
    StoreApiGatewayTimeoutError,
    StoreApiInternalError,
    StoreApiNotImplementedError,
    StoreApiResourceNotFound,
    StoreApiResponseDecodeError,
    StoreApiResponseError,
    StoreApiResponseErrorList,
    StoreApiServiceUnavailableError,
)


logger = logging.getLogger(__name__)


def _sanitize_dict(dictionary):
    result = {}
    for k, v in dictionary.items():
        if isinstance(v, str):
            result[k] = f"<len {len(v)}>"
        else:
            result[k] = None
    return result


def _get_request_body(request) -> str:
    body = request.body
    if isinstance(body, (bytes, bytearray)):
        # try to decode utf-8
        try:
            body = body.decode()
        except UnicodeError:
            # we don't want to guess so we just print the body's length
            body = f"<len {len(body)}>"
    elif not isinstance(body, str):
        # we don't know if the type will be JSON serializable
        # so we just print the type
        body = f"{type(body)}"
    return body


def _loggable_request(request):
    return {
        "url": request.url,
        "headers": _sanitize_dict(request.headers),
        "cookies": _sanitize_dict(request._cookies),
        "body": _get_request_body(request),
    }


def _loggable_response(response):
    return {
        "status": response.status_code,
        "url": response.url,
        "headers": _sanitize_dict(response.headers),
        "cookies": _sanitize_dict(response.cookies),
        "text": response.text,
    }


class Base:
    def __init__(self, session):
        self.session = session

    def log_detailed_error(self, response):
        logger.error(
            "Request failed",
            extra={
                "request": _loggable_request(response.request),
                "response": _loggable_response(response),
            },
        )

    def process_response(self, response):
        # 5xx responses are not in JSON format
        if response.status_code >= 500:
            self.log_detailed_error(response)
            if response.status_code == 500:
                raise StoreApiInternalError("Internal error upstream")
            elif response.status_code == 501:
                raise StoreApiNotImplementedError(
                    "Service doesn't implement this method"
                )
            elif response.status_code == 502:
                raise StoreApiBadGatewayError("Invalid response from upstream")
            elif response.status_code == 503:
                raise StoreApiServiceUnavailableError("Service is unavailable")
            elif response.status_code == 504:
                raise StoreApiGatewayTimeoutError("Upstream request timed out")
            else:
                raise StoreApiConnectionError(
                    f"Service unavailable, code {response.status_code}"
                )

        try:
            body = response.json()
        except ValueError as decode_error:
            logger.error(
                "JSON decoding failed. Response text: %s", response.text
            )
            api_error_exception = StoreApiResponseDecodeError(
                "JSON decoding failed: {}".format(decode_error)
            )
            raise api_error_exception

        if self._is_macaroon_expired(response.headers):
            logger.error("Publisher macaroon refresh required")
            raise PublisherMacaroonRefreshRequired

        if not response.ok:
            self.log_detailed_error(response)
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
