import arrowhead_client as ar

def test_arrowhead_system():
    test_consumer = ar.ArrowheadSystem(
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
    assert test_consumer.url == '127.0.0.1:0'

