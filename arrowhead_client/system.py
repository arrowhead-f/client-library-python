from typing import Dict, Union
from dataclasses import dataclass


@dataclass
class ArrowheadSystem:
    """ Basic Arrowhead ArrowheadSystem class """

    system_name: str
    address: str
    port: int
    authentication_info: str

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
