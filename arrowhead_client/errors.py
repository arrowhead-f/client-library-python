
class ArrowheadError(Exception):
    pass

class CouldNotRegisterServiceError(ArrowheadError):
    def __init__(self, service_definition: str, error_message: str, message=''):
        self.error_message = error_message
        self.service_definition = service_definition
        self.message = message
        super().__init__(self.error_message + message)

    def __str__(self) -> str:
        return f'Could not register service \'{self.service_definition}\': {self.error_message} '

class CouldNotUnregisterServiceError(ArrowheadError):
    def __init__(self, service_definition: str, error_message: str, message: str=''):
        self.error_message = error_message
        self.service_definition = service_definition
        self.message = message
        super().__init__(self.error_message)

    def __str__(self) -> str:
        return f'Could not unregister service \'{self.service_definition}\': {self.error_message} '

class NotAuthorizedError(ArrowheadError):
    def __init__(self, message: str=''):
        self.message = message
        super().__init__(self.message)

class CoreServiceNotAvailableError(ArrowheadError):
    def __init__(self, core_service: str, message: str=''):
        self.core_service = core_service
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f'{self.core_service} not available: {self.message}'

class NoAvailableServicesError(ArrowheadError):
    def __init__(self, message: str=''):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f'No orchestration rules available for service: {self.message}'