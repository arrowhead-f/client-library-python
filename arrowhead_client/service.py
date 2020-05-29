from typing import Callable, Union, Optional, Dict
from collections import namedtuple
from .utils import ServiceInterface

Cert = namedtuple('Cert', ['certfile', 'keyfile'])


class Service():
    """ Base class for services """

    def __init__(self,
                 service_definition: str,
                 service_uri: str,
                 interface: Union[str, ServiceInterface]) -> None:
        self.service_definition = service_definition
        self.service_uri = service_uri
        if isinstance(interface, str):
            self.interface = ServiceInterface.from_str(interface)
        else:
            self.interface = interface

    def __repr__(self) -> str:
        variable_string = ', '.join([f'{str(key)}={str(value)}' for key, value in vars(self).items()])
        return f'{self.__class__.__name__}({variable_string})'

