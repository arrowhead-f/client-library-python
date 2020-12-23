from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Dict, Optional

from arrowhead_client.dto import DTOMixin
from arrowhead_client.common_constants import SecurityInfo, AccessPolicies


@dataclass()
class ServiceInterface:
    """
    Service interface triple class.

    Attributes:
        protocol: Protocol description.
        secure: Security information description.
        payload: Payload format description.
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
        """
        Construct a ServiceInterface from a string representation.

        Args:
            interface_str: string representation of type 'PROTOCOL-SECURE-PAYLOAD'
        Returns:
            ServiceInterface from string description.
        Raises:
            TypeError if interface string is malformed.
        """
        try:
            return cls(*interface_str.split('-'))
        except TypeError as e:
            raise ValueError(f'Malformed service interface string: \'{interface_str}\'.') from e

    @classmethod
    def with_access_policy(cls, protocol, access_policy, payload):
        """
        Construct a ServiceInterface similar to the normal constructor,
        but using the name of an access policy instead of 'SECURE' or 'INSECURE'

        Args:
            protocol: Protocol supported by service.
            access_policy: Access policy.
            payload: Payload type.
        Returns:
            ServiceInterface from string description.
        """
        if access_policy == AccessPolicies.UNRESTRICTED:
            return cls(protocol, SecurityInfo.INSECURE, payload)
        return cls(protocol, SecurityInfo.SECURE, payload)

    def dto(self) -> str:
        return '-'.join(vars(self).values())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            try:
                other = ServiceInterface.from_str(other)
            except TypeError:
                return False
        elif isinstance(other, ServiceInterface):
            other = other
        else:
            raise TypeError('other must be of type ServiceInterface or str')

        return self.protocol == other.protocol and \
               self.secure == other.secure and \
               self.payload == other.payload


DTOMixin.register(ServiceInterface)


class Service:
    """
    Arrowhead Service class.

    Attributes:
        service_definition: Service definition as :code:`str`.
        service_uri: Service uri location as :code:`str`.
        interface: Service interface triple, given as :code:`str` (ex. :code:`'HTTP-SECURE-JSON'`) or as :code:`ServiceInterface`.
        access_policy: Access policy for the service, needs to be one of `NOT_SECURE`, `CERTIFICATE`, or `TOKEN`.
        metadata: Metadata provided in a json-compliant dictionary.
        version: Service version.
    """

    def __init__(self,
                 service_definition: str,
                 service_uri: str = '',
                 interface: Union[str, ServiceInterface] = '',
                 access_policy: str = AccessPolicies.CERTIFICATE,
                 metadata: Dict = None,
                 version: Optional[int] = None) -> None:
        self.service_definition = service_definition
        self.service_uri = service_uri
        if interface and isinstance(interface, str):
            # TODO: Why did I put this try except block here? It doesn't seem to have much use.
            try:
                self.interface = ServiceInterface.from_str(interface)
            except TypeError:
                # TODO: This should error should just be left uncaught?
                self.interface = ''
        else:
            self.interface = interface
        self.access_policy = access_policy
        self.metadata = metadata
        self.version = version

    # TODO: Write good repr
    #def __repr__(self) -> str:
    #    variable_string = ', '.join([f'{str(key)}={str(value)}'
    #                                 for key, value in vars(self).items()])
    #    return f'{self.__class__.__name__}({variable_string})'

    def __eq__(self, other):
        # TODO: this is a rudimentary __eq__, this class should probably be a dataclass instead
        return vars(self) == vars(other)
