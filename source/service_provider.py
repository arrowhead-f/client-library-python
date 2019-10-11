from flask import Flask, url_for, request
import requests

from .arrowhead_system import ArrowheadSystem
from . import utils

from dataclasses import asdict
from functools import wraps
from pprint import pprint

class ServiceProvider:
    """ Arrowhead service provider class """
    def __init__(self, 
            name='default', 
            service_uri='',
            metadata=None,
            interfaces='',
            provider_system = None,
            consumer_system = None,
            provider_name = 'Default',
            address = '127.0.0.1',
            port = '8080',
            service_registry=None):

        if provider_system:
            self.provider_system = provider_system
        else:
            self.provider_system = ArrowheadSystem(
                    systemName = provider_name,
                    address = address,
                    port = port)
            #self.consumer_system = consumer_system
        self.name = name
        self.uri = service_uri
        if metadata:
            self.metadata = metadata
        else:
            self.metadata = {}
        self.service_routes = []
        self.service = Flask(self.name)
        self.sr_entry = self.make_sr_entry()

        if consumer_system:
            self.consumer_system = consumer_system
        else:
            self.consumer_system = None

        assert service_registry
        self.service_registry = service_registry

        self.orchestrator, self.authorization = None, None #utils.find_core_systems(self.service_registry)

    def add_route(self, method_uri="", func=None, rest_methods=None, **kwargs):
        """ Adds routes for functions """
        if not rest_methods:
            methods = ['GET']
        else:
            methods = rest_methods
        print(methods)
        @self.service.route(f'{self.uri}{method_uri}', methods=methods)
        @wraps(func)
        def func_wrapper():
            return func(**kwargs)

    def _auth_entry(self):
        """ Creates authentication entry """
        try:
            assert self.consumer_system
        except AssertionError:
            print('Consumer system must be defined for creation of athentication entry')

        auth_entry = {
                'consumer': self.consumer_system.no_auth,
                'providerList': [self.provider_system.no_auth],
                'serviceList': [{
                    'serviceDefinition': self.name,
                    'interfaces': [],
                    'serviceMetadata': self.metadata
                    }]
                }

        return auth_entry

    def make_sr_entry(self):
        """ Create sr_entry, only for internal use """

        sr_entry = {
                'serviceDefinition': self.name,
                #'providedService': {
                    #'serviceDefinition': self.name,
                    #'interfaces': [],
                    #'serviceMetadata': self.metadata
                    #},
                # Filter out authentication info
                'providerSystem': asdict(self.provider_system),
                'serviceURI': self.uri,
                'interfaces': ['HTTP-INSECURE-JSON'],
                'secure': "NOT_SECURE"
                }
        return sr_entry

    def authenticate(self):
        """authenticate service"""
        print('Authentication entry')
        pprint(self._auth_entry())
        r = requests.post('http://{self.authorization.address}:{self.authorization.port}/authorization/mgmt/intracloud', json=self._auth_entry())
        pprint(r.json())
        assert r.ok

    def publish(self):
        """ Publish service """
        r = requests.post(f'http://{self.service_registry.address}:{self.service_registry.port}/serviceregistry/register', json=self.sr_entry)
        pprint(r.json())
        assert r.ok

    def unpublish(self):
        """ Unpublish service """
        params = {
                'service_definition': self.name,
                'system_name': self.provider_system.systemName,
                'address': self.provider_system.address,
                'port': self.provider_system.port
                }
        r = requests.delete(f'http://{self.service_registry.address}:{self.service_registry.port}/serviceregistry/unregister', params=params)
        assert r.ok

    def run(self, auth=False):
        """ Authenticate """
        if auth:
            self.authenticate()

        """ Publish """
        self.publish()

        """ Run the service """
        self.service.run(host=self.provider_system.address, 
                port=self.provider_system.port)

        """ Unpublish """
        self.unpublish()

if __name__=='__main__':
    """ A bunch of test code """
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8443')
    test_system = ArrowheadSystem(systemName='Test', address='127.0.0.1', port='9345')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')
    test_provider = ServiceProvider(service_uri='/TestProvider', provider_system=test_system, consumer_system=test_consumer)
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
