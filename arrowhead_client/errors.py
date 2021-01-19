class ArrowheadError(Exception):
    """ Base exception for arrowhead-client expections. """


class CoreServiceInputError(ArrowheadError):
    """ Exception raised when core service returns status 400. """


class OrchestrationError(ArrowheadError):
    pass


class AuthorizationError(ArrowheadError):
    pass


class NotAuthorizedError(AuthorizationError):
    """ Exception raised when provider returns status 401 or 403. """


class MalformedTokenError(AuthorizationError):
    """ Exception raised when received authorization token is malformed. """


class InvalidTokenError(AuthorizationError):
    """ Exception raised when received authorization token is invalid. """


class CoreServiceNotAvailableError(ArrowheadError):
    """ Exception raised when core service returns 500. """


class NoAvailableServicesError(ArrowheadError):
    pass
