from dataclasses import dataclass

@dataclass
class ArrowheadSystem():
    system_name: str = 'Default'
    address: str = 'localhost'
    port: str = '8080'
    authentication_info: str = ''
    
if __name__ == '__main__':
    test_system = ArrowheadSystem()
    clone_system = ArrowheadSystem()
    false_name_system = ArrowheadSystem(system_name='default')
    false_addr_system = ArrowheadSystem(address='0.0.0.0')
    false_port_system = ArrowheadSystem(port='8081')
    print(test_system)

    print(test_system == test_system)
    print(test_system == clone_system)
    print(test_system == false_name_system)
    print(test_system == false_addr_system)
    print(test_system == false_port_system)
