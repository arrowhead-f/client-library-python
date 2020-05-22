from dataclasses import dataclass


@dataclass
class ArrowheadSystem:
    """ Basic Arrowhead System class """

    system_name: str
    address: str
    port: str
    authentication_info: str

    @property
    def url(self):
        return f'{self.address}:{self.port}'

    @property
    def dto(self):
        return_dto = {
            'systemName': self.system_name,
            'address': self.address,
            'port': self.port,
            'authenticationInfo': self.authentication_info}
        return return_dto


if __name__ == '__main__':
    pass
