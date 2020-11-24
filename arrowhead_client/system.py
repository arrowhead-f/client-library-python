from typing import Dict, Union, Optional
from dataclasses import dataclass, field
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from arrowhead_client.security import create_authentication_info


@dataclass
class ArrowheadSystem:
    """
    ArrowheadSystem class.

    Args:
        system_name: System name as :code:`str`.
        address: IP address as :code:`str`.
        port: Port as :code:`int`.
        authentication_info: Authentication info as :code:`str`.
    """

    system_name: str
    address: str
    port: int
    _privatekey: Optional[RSAPrivateKey] = field(default=None)
    _publickey: Optional[RSAPublicKey] = field(default=None)

    @property
    def authentication_info(self):
        return create_authentication_info(self._publickey)

    @property
    def authority(self):
        return f'{self.address}:{self.port}'

    @property
    def dto(self):
        system_dto = {
                'systemName': self.system_name,
                'address': self.address,
                'port': self.port,
                'authenticationInfo': self.authentication_info}
        return system_dto

    @classmethod
    def from_dto(cls, system_dto: Dict[str, Union[int, str]]):
        return cls(
                system_name=str(system_dto['systemName']),
                address=str(system_dto['address']),
                port=int(system_dto['port']),
                authentication_info=str(system_dto['authenticationInfo'])
        )
