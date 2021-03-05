from arrowhead_client.service import Service as ConsumedHttpService, ServiceInterface

def test_can_instantiate():
    test = ConsumedHttpService('test_service', 'test', ServiceInterface.from_str('HTTP-SECURE-JSON'))

