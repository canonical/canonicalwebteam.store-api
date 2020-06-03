class StoreApiError(Exception):
    """
    Base exception for any errors in the API layer
    """

    pass


class StoreApiConnectionError(StoreApiError):
    """
    Communication with the API failed
    """

    pass


class StoreApiTimeoutError(StoreApiError):
    """
    Communication with the API timed out
    """

    pass


class StoreApiResponseDecodeError(StoreApiError):
    """
    We failed to properly decode the response from the API
    """

    pass


class StoreApiResponseError(StoreApiError):
    """
    The API responded with an error
    """

    def __init__(self, message, status_code):
        self.status_code = status_code
        return super().__init__(message)


class StoreApiResponseErrorList(StoreApiResponseError):
    """
    The API responded with a list of errors,
    which are included in self.errors
    """

    def __init__(self, message, status_code, errors):
        self.errors = errors
        return super().__init__(message, status_code)


class StoreApiCircuitBreaker(StoreApiError):
    pass


class PublisherAgreementNotSigned(StoreApiError):
    """
    The user needs to sign the agreement
    """

    pass


class PublisherMissingUsername(StoreApiError):
    """
    The user hasn't registed a username
    """

    pass


class PublisherMacaroonRefreshRequired(StoreApiError):
    """
    The macaroon needs to be refreshed
    """

    pass
