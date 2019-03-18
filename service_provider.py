from flask import Flask, url_for
import requests

from pprint import pprint

class ServiceProvider:
    """ Arrowhead service provider class """
    def __init__(self, 
            name='default', 
            host='localhost', 
            service_uri='',
            port='8080',
            metadata=dict(),
            interfaces='',
            system_name='Default'):

        self.host = host
        self.port = port
        self.name = name
        self.uri = service_uri
        self.system_name = system_name
        self.metadata = metadata
        self.service_routes = []
        self.service = Flask(__name__)
        self.sr_entry = self._sr_entry()

    def add_route(self, function_uri="", func=None, **kwargs):
        """ Adds routes for functions """
        @self.service.route(f'{self.uri}{function_uri}')
        def func_wrapper():
            return func(**kwargs)

    def _auth_entry(self):
        """ Creates authentication entry """

        auth_entry = {
            'consumer': {
                'systemName': 'SomeClient',
                'address': '0.0.0.0',
                'port': '8081'
            },
            'providerList': [{
                'systemName': self.system_name,
                'address': self.host,
                'port': self.port
            }],
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
            'provider' : {
                'systemName': self.system_name,
                'address': self.host,
                'port': self.port,
            },
            'serviceUri': self.uri,
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
        self.service.run(host=self.host, port=self.port)

        """ Unpublish """
        self.unpublish()

if __name__=='__main__':
    """ A bunch of test code """
    test_provider = ServiceProvider(service_uri='/TestProvider')
    print(test_provider.service)
    pprint(test_provider.sr_entry)
    print(type(test_provider.sr_entry))
    def hello(name):
        return f'hello {name}\n'

    test_provider.add_route(function_uri='/test', func=hello, name='Jacob')
    print(test_provider.service_routes)

    test_provider.run(auth=True)
