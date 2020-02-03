from source.arrowhead_system import ArrowheadSystem
from source.provider import Provider
#from source.service_provider import ServiceProvider
import datetime
from pprint import pprint

'''
class TestProvider(Provider, ArrowheadSystem):
    def __init__(
'''

if __name__=='__main__':
    """ A bunch of test code """
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8443')
    test_system = ArrowheadSystem(systemName='Test', address='127.0.0.1', port='9345')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')

    test_provider_2 = TestProvider(name='Test_2', service_uri='/TestProvider', provider_system=test_system, response_string='Hai', service_registry=service_registry)

    test_provider_2.run(auth=False)
