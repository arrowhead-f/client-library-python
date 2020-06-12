from arrowhead_client.system import ArrowheadSystem

valid_keys = {
    'systemName',
    'address',
    'port',
    'authenticationInfo'
}

def test_arrowhead_system():
    test_system = ArrowheadSystem(
            'test_system',
            '127.0.0.1',
            0,
            '',
    )


    assert test_system.dto.keys() == valid_keys
    assert test_system.authority == '127.0.0.1:0'

def test_from_dto():
    dto = {
        "systemName": "test_system",
        "address": "127.0.0.1",
        "port": 0,
        "authenticationInfo": "look away"
    }

    test_system = ArrowheadSystem.from_dto(dto)

    assert test_system.dto.keys() == valid_keys
    assert test_system.authority == '127.0.0.1:0'
    assert test_system.system_name == 'test_system'
    assert test_system.authentication_info == 'look away'

