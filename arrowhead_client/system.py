from dataclasses import dataclass


@dataclass
class ArrowheadSystem:
    """ Basic Arrowhead System class """

    system_name: str
    address: str
    port: int
    authentication_info: str

    @property
    def authority(self):
        return f'{self.address}:{self.port}'

    #TODO: from_dto() constructor
    @property
    def dto(self):
        return_dto = {
            'systemName': self.system_name,
            'address': self.address,
            'port': self.port,
            'authenticationInfo': self.authentication_info}
        return return_dto