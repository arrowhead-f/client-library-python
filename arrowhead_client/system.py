from typing import Dict

from arrowhead_client.dto import DTOMixin
from arrowhead_client.security.utils import cert_to_authentication_info


class ArrowheadSystem(DTOMixin):
    """
    ArrowheadSystem class.

    Attributes:
        system_name: System name.
        address: IP address.
        port: Port.
        authentication_info: Authentication info.
    """

    system_name: str
    address: str
    port: int
    authentication_info: str = ''

    @property
    def authority(self):
        return f'{self.address}:{self.port}'

    @classmethod
    def from_dto(cls, system_dto: Dict):
        return cls(
                system_name=str(system_dto['systemName']),
                address=str(system_dto['address']),
                port=int(system_dto['port']),
                authentication_info=str(system_dto.get('authenticationInfo', '')),
        )

    @classmethod
    def with_certfile(
            cls,
            system_name: str,
            address: str,
            port: int,
            certfile: str,
    ) -> 'ArrowheadSystem':
        authentication_info = cert_to_authentication_info(certfile)

        return cls(
                system_name=system_name,
                address=address,
                port=port,
                authentication_info=authentication_info
        )
