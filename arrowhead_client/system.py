"""
=============
System Module
=============
"""
from typing import Dict

from arrowhead_client.dto import DTOMixin
from arrowhead_client.security.utils import cert_to_authentication_info


class ArrowheadSystem(DTOMixin):
    """
    ArrowheadSystem class, inherits from :py:class:`~arrowhead_client.dto.DTOMixin`, which makes it a subclass of :py:class:`pydantic.BaseModel`.
    This makes ``__init__`` have different behaviour, which is described in the links above.

    This class is a data container for data related to a system in an Arrowhead local cloud.
    It should not be necessary to create instances of this class outside of sending data between systems.

    Args:
        system_name (str): System name.
        address: URL or IP address.
        port: Port.
        authentication_info (str): Authentication info.
        systemName: Alias of system_name.
        authenticationInfo: Alias of authentication_info
    """

    system_name: str
    address: str
    port: int
    authentication_info: str = ''

    @property
    def authority(self):
        return f'{self.address}:{self.port}'

    @classmethod
    def make(
            cls,
            system_name: str,
            address: str,
            port: int,
            authentication_info: str = '',
    ):
        """
        Creates a new instance of ArrowheadSystem without needing to use keyword arguments.

        Args:
            system_name: Name of the system.
            address: Address of the system.
            port: Port of the system.
            authentication_info: PEM string representing the certificate used by the client owning the system.
        Return:
            Instantiated ArrowheadSystem.

        Example::

            from arrowhead_client.system import ArrowheadSystem

            # Create an ArrowheadSystem without an authentication info string.
            example_system = ArrowheadSystem.make(
                    'example_system',
                    '127.0.0.1',
                    5678,
            )
        """
        return cls(
                system_name=system_name,
                address=address,
                port=port,
                authentication_info=authentication_info
        )

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
        """
        Creates a new ArrowheadSystem similarly to ArrowheadSystem.make(), but automatically constructs the
        authentication info from a certificate file.

        Args:
            system_name: Name of the system.
            address: Address of the system.
            port: Port of the system.
            certfile: PEM certificate file.
        Return:
            Instantiated ArrowheadSystem.

        Example::

            from arrowhead_client.system import ArrowheadSystem

            # Create a new instance of ArrowheadSystem and automatically generate
            # authentication string from a certificate.
            example_system = ArrowheadSystem.with_certfile(
                    'example_system',
                    '127.0.0.1',
                    5678,
                    'certificates/example_system.crt',
            )
        """
        authentication_info = cert_to_authentication_info(certfile)

        return cls(
                system_name=system_name,
                address=address,
                port=port,
                authentication_info=authentication_info
        )
