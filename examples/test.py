from source.arrowhead_system import ArrowheadSystem
from source.service_provider import ServiceProvider
import datetime
from pprint import pprint

class TestProvider(ServiceProvider):
    def __init__(self, 
            provider_system, 
            name,
            service_uri,
            service_registry,
            response_string):
        super(TestProvider, self).__init__(
                provider_system=provider_system, 
                name=name, 
                service_uri=service_uri,
                service_registry=service_registry)
        self.response_string = response_string

    """
    @add_method(self)
    def response():
        print(self.response_string)
    """
    @ServiceProvider.add_method(method_uri='/test')
    def response(self):
        print(self.response_string)

if __name__=='__main__':
    """ A bunch of test code """
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8443')
    test_system = ArrowheadSystem(systemName='Test', address='127.0.0.1', port='9345')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')
    #test_provider = ServiceProvider(service_uri='/TestProvider', provider_system=test_system, consumer_system=test_consumer, service_registry=service_registry)
    #pprint(test_provider.sr_entry)
    #def hello(name):
        #return f'hello {name}\n'
    #test_provider.add_route(method_uri='/test', func=hello, name='Jacob')

    #test_provider.run(auth=False)

    test_provider_2 = TestProvider(name='Test_2', service_uri='/TestProvider', provider_system=test_system, response_string='Hai', service_registry=service_registry)

    test_provider_2.run(auth=False)
