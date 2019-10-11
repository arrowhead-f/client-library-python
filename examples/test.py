from source.arrowhead_system import ArrowheadSystem
from source.service_provider import ServiceProvider
import datetime
from pprint import pprint

if __name__=='__main__':
    """ A bunch of test code """
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8443')
    test_system = ArrowheadSystem(systemName='Test', address='127.0.0.1', port='9345')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')
    test_provider = ServiceProvider(service_uri='/TestProvider', provider_system=test_system, consumer_system=test_consumer, service_registry=service_registry)
    pprint(test_provider.sr_entry)
    def hello(name):
        return f'hello {name}\n'

    test_provider.add_route(method_uri='/test', func=hello, name='Jacob')
    #print(test_provider.service_routes)
    test_provider.publish()
    input()
    test_provider.unpublish()
    '''
    test_provider.run(auth=False)
    '''
