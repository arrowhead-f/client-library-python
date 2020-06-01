from arrowhead_client.system import ArrowheadSystem

def test_arrowhead_system():
    test_consumer = ArrowheadSystem(
            'test_consumer',
            '127.0.0.1',
            0,
            '',
    )

    valid_keys = {
        'systemName',
        'address',
        'port',
        'authenticationInfo'
    }

    assert test_consumer.dto.keys() == valid_keys
    assert test_consumer.authority == '127.0.0.1:0'

