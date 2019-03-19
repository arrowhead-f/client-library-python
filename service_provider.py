from flask import Flask, url_for
import requests

from arrowhead_system import ArrowheadSystem

from dataclasses import asdict
from pprint import pprint

class ServiceProvider:
    """ Arrowhead service provider class """
    def __init__(self, 
            name='default', 
            service_uri='',
            metadata=dict(),
            interfaces='',
            provider_system = None,
            provider_name = 'Default',
            address = '127.0.0.1',
            port = '8080'):

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
        self.metadata = metadata
        self.service_routes = []
        self.service = Flask(__name__)
        self.sr_entry = self._sr_entry()

    def add_route(self, function_uri="", func=None, **kwargs):
        """ Adds routes for functions """
        @self.service.route(f'{self.uri}{function_uri}')
        def func_wrapper():
            return func(**kwargs)

    def _extract_keys(self, ArrowheadSystem):
        """ Returns the dictionary form of an ArrowheadSystem without
        the authenticationInfo key and value """

        keys = ['systemName', 'address', 'port']
        return {key: asdict(ArrowheadSystem)[key] for key in keys}

    def _auth_entry(self):
        """ Creates authentication entry """

        auth_entry = {
            'consumer': {
                'systemName': 'SomeClient',
                'address': '0.0.0.0',
                'port': '8081'
            },
            'providerList': [self._extract_keys(self.provider_system)],
            'serviceList': [{
                'serviceDefinition': self.name,
                'interfaces': [],
                'serviceMetadata': self.metadata
            }]
        }

        return auth_entry

    def _sr_entry(self):
        """ Create sr_entry, only for internal use """

        sr_entry = {
            'providedService': {
                'serviceDefinition': self.name,
                'interfaces': [],
                'serviceMetadata': self.metadata
            },
            # Filter out authentication info
            'provider': self._extract_keys(self.provider_system),
            'serviceURI': self.uri,
            'version': 0.0
        }
        return sr_entry
    
    def authenticate(self):
        """authenticate service"""
        pprint(f'authenticate: {self._auth_entry()}')
        r = requests.post('http://127.0.0.1:8444/authorization/mgmt/intracloud', json=self._auth_entry())
        assert r.ok
    
    def publish(self):
        """ Publish service """
        r = requests.post('http://127.0.0.1:8442/serviceregistry/register', json=self.sr_entry)
        assert r.ok
    
    def unpublish(self):
        """ Unpublish service """
        r = requests.put('http://127.0.0.1:8442/serviceregistry/remove', json=self.sr_entry)
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
    test_provider = ServiceProvider(service_uri='/TestProvider')
    pprint(test_provider.sr_entry)
    def hello(name):
        return f'hello {name}\n'

    test_provider.add_route(function_uri='/test', func=hello, name='Jacob')
    print(test_provider.service_routes)

    test_provider.run(auth=True)
