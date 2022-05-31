from __future__ import annotations

class ArrowheadError(Exception):
    """ Base exception for arrowhead-client expections. """


class ServiceConnectionError(ArrowheadError):
    """Exception rased when service connection cannot be established."""
    def __init__(self, service_definition: str, system_name: str, endpoint: str, message: str = ""):
        self.service_definition = service_definition
        self.system_name = system_name
        self.endpoint = endpoint
        self.message = message
        super().__init__(message)

    def __str__(self):
        standard_text = f'Error occured when consuming service "{self.service_definition}" from system "{self.system_name}" at {self.endpoint}'
        extra_text = f": {self.message}." if self.message else "."

        return standard_text + extra_text


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
