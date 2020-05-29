from arrowhead_client.service import Service as ConsumedHttpService

def test_can_instantiate():
    test = ConsumedHttpService('test_service', 'test', 'HTTP-SECURE-JSON')

