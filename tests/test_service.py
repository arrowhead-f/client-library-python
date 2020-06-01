from arrowhead_client import service

def test_interface():
    test_interface = service.ServiceInterface(
            'HTTP',
            'SECURE',
            'JSON',
    )
    test_interface_lower = service.ServiceInterface(
            'http',
            'SeCuRe',
            'jSON',
    )

    assert test_interface == 'HTTP-SECURE-JSON'
    assert test_interface == service.ServiceInterface.from_str('HTTP-SECURE-JSON')
    assert test_interface.dto == 'HTTP-SECURE-JSON'
    assert test_interface_lower == test_interface
