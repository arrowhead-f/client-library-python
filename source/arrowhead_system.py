from dataclasses import dataclass, field, asdict

@dataclass
class ArrowheadSystem():
    systemName: str = 'Default'
    address: str = 'localhost'
    port: str = '8080'
    authenticationInfo: str = field(compare=False, default='')

    @property
    def no_auth(self):
        return {'systemName': self.systemName,
                'address': self.address,
                'port': self.port}

if __name__ == '__main__':
    test_system = ArrowheadSystem()
    clone_system = ArrowheadSystem()
    wrong_system = ArrowheadSystem(port=8080)
    false_name_system = ArrowheadSystem(system_name='default')
    false_addr_system = ArrowheadSystem(address='0.0.0.0')
    false_port_system = ArrowheadSystem(port='8081')
    other_auth_system = ArrowheadSystem(authentication_info = 'test')
    print(test_system)
    print(clone_system)
    print(wrong_system)

    print(test_system == test_system)
    print(test_system == clone_system)
    print(test_system == false_name_system)
    print(test_system == false_addr_system)
    print(test_system == false_port_system)
    print(test_system == other_auth_system)

    print(asdict(test_system))
