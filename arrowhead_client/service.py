from typing import Callable, Any, Union, Optional
from collections import namedtuple
from abc import ABC, abstractmethod
from .utils import ServiceInterface

Cert = namedtuple('Cert', ['certfile', 'keyfile'])


class BaseService(ABC):
    """ Base class for services """

    def __init__(self,
                 service_definition: str,
                 service_uri: str,
                 interface: Union[str, ServiceInterface],
                 address: str,
                 port: str) -> None:
        self.service_definition = service_definition
        self.service_uri = service_uri
        self.address = address
        self.port = port
        if isinstance(interface, str):
            self.interface = ServiceInterface.from_str(interface)
        else:
            self.interface = interface

    @property
    def url(self) -> str:
        """ Service address and port """
        return f'https://{self.address}:{self.port}/{self.service_uri}'

    def __repr__(self) -> str:
        variable_string = ', '.join([f'{str(key)}={str(value)}' for key, value in vars(self).items()])
        return f'{self.__class__.__name__}({variable_string})'


class ConsumedHttpService(BaseService):
    """ Consumed HTTP service """

    # TODO: Give this class a nice __repr__ and __str__
    def __init__(self,
                 service_definition: str,
                 service_uri: str,
                 interface: Union[str, ServiceInterface],
                 address: str,
                 port: str,
                 http_method: Optional[Callable],
                 post_processing: Optional[Callable] = None, ) -> None:
        super().__init__(service_definition, service_uri, interface, address, port)
        self.http_method = http_method
        self.post_processing = post_processing

    def consume(self, *args, cert, **kwargs) -> object:
        """ Call the service """

        if callable(self.http_method):
            # TODO: Add error handling
            response = self.http_method(self.url, *args, cert=cert, verify=False, **kwargs)
        else:
            raise RuntimeError(f'{self} consumed before .method is set.')

        if self.interface.payload == 'JSON':
            response = response.json()

        # Test if post processing hook exists and is callable
        if callable(self.post_processing):
            response = self.post_processing(response)
            # TODO: Add warning if object is not callable, it's probably a user error

        return response

    def __str__(self) -> str:
        # ConsumedHttpService at https://examp.le:1234/service
        return f'{self.__class__.__name__}({self.service_definition}) looking at {self.url}'


class ProvidedHttpService(BaseService):
    """ Provided HTTP service class """

    def __init__(self,
                 service_definition: str,
                 service_uri: str,
                 interface: Union[str, ServiceInterface],
                 address: str,
                 port: str,
                 http_method: str,
                 provides: Optional[Callable] = None, ) -> None:
        super().__init__(service_definition, service_uri, interface, address, port)
        self.http_method = http_method
        self.provides = provides

    @property
    def url(self) -> str:
        """ Shortcut for the full service url """
        return f'https://{self.address}:{self.port}/{self.service_uri}'

    def register(self, service_function: Callable, provider_system: Any) -> None:  # type: ignore
        """ Register service with provider system """
        raise NotImplementedError
        # This method seemingly does nothing, and I am not sure why I added it, it raises an error for now
        # TODO: Remove this method?
        self.address = provider_system.address
        self.port = provider_system.port
        self.provides = service_function
        provider_system.provided_services[self.service_definition] = self

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.service_definition}) at {self.url}'

    def __repr__(self) -> str:
        variable_string = ', '.join([f'{str(key)}={str(value)}' for key, value in vars(self).items()])
        return f'{self.__class__.__name__}({variable_string})'


if __name__ == '__main__':
    pass
