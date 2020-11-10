from __future__ import annotations
from dataclasses import dataclass
from typing import Union


@dataclass()
class ServiceInterface:
    """
    Service interface triple class
    """

    protocol: str
    secure: str
    payload: str

    def __post_init__(self):
        self.protocol = self.protocol.upper()
        self.secure = self.secure.upper()
        self.payload = self.payload.upper()

    @classmethod
    def from_str(cls, interface_str: str) -> ServiceInterface:
        return cls(*interface_str.split('-'))

    @property
    def dto(self) -> str:
        return '-'.join(vars(self).values())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            other = ServiceInterface.from_str(other)
        elif isinstance(other, ServiceInterface):
            other = other
        else:
            raise ValueError('Other must be of type ServiceInterface or str')

        return self.protocol == other.protocol and \
               self.secure == other.secure and \
               self.payload == other.payload


class Service():
    """
    Arrowhead Service class.

    Args:
        service_definition: service definition as :code:`str`.
        service_uri: service uri location as :code:`str`.
        interface: service interface triple, given as :code:`str` (ex. :code:`'HTTP-SECURE-JSON'`) or as :code:`ServiceInterface`.
    """

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
        # TODO: Add security/access policy, metadata, and version fields.

    def __repr__(self) -> str:
        variable_string = ', '.join([f'{str(key)}={str(value)}' for key, value in vars(self).items()])
        return f'{self.__class__.__name__}({variable_string})'
