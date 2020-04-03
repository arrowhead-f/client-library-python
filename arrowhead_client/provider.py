import inspect
from abc import ABC, abstractmethod
from flask import Flask
from gevent import pywsgi
import requests
from functools import wraps
import functools
from .service import ProvidedService

def provided_service(service_definition, service_uri, interfaces, secure='CERTIFICATE'):
    if secure.upper() != 'CERTIFICATE':
        self.logger.error(f'Secure in definition of \'{service_definition}\' is not \'CERTIFICATE\'')
        raise ValueError('CERTIFICATE is currently the only supported security')

    def middle(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.services[service_definition] = ProvidedService(
                    service_definition, service_uri, interfaces, secure, func)
            self.app.add_url_rule(service_uri, service_definition, func)
            print('hej')
            exit()
            return func(self, *args, **kwargs)
        return wrapper

    middle.service_setup = True

    return middle

class BaseProvider(ABC):
    ''' Mixin class for service provision '''
    def __init__(self):
        self.app = Flask(__name__)
        # Add logging handlers for flask (DOES NOT WORK CURRENTLY)
        for handler in self.logger.handlers:
            self.app.logger.addHandler(handler)
        self.services = {}
        self.setup_echo()
        self.server = pywsgi.WSGIServer((self.address, int(self.port)), self.app,
                keyfile=self.keyfile, certfile=self.certfile,
                log=self.logger)

        #self.setup_services()

    def setup_echo(self):
        @self.add_service('echo', '/echo', 'HTTP-SECURE-JSON')
        def echo():
            return 'Got it!'

    def add_service(self, service_definition, service_uri, interfaces, methods=None, secure='CERTIFICATE'):
        '''
        Decorator that adds services to the Arrowhead system, usage example:
        @ArrowheadSystem.add_service(*dec_args)
        def foo_service(*args)
            ...

        :param service_definition: Service definition registered in the service registry
        :type service_definition: str
        :param service_uri: Location of service
        :type service_uri: str
        :param interfaces: The supported interfaces of the service
        :type interfaces: str
        :param secure: Security supported by the service (currently CERTIFICATE only)
        :type secure: str

        :returns: The decorated function, now bound to a uri
        :rtype: func
        '''
        if secure.upper() != 'CERTIFICATE':
            self.logger.error(f'Secure in definition of \'{service_definition}\' is not \'CERTIFICATE\'')
            raise ValueError('CERTIFICATE is currently the only supported security')

        if methods == None:
            methods = ['Get']

        def decorator(f):
            self.services[service_definition] = ProvidedService(
                    service_definition, service_uri, interfaces, secure, f)
            self.app.add_url_rule(service_uri, service_definition, f, methods=methods)

            return f

        return decorator

    '''
    @abstractmethod
    def setup_services(self):
        pass
    '''

    def register_service(self, service):
        '''
        Registers the given service with service registry

        :param service: Service to be registered
        :param type: ProvidedService
        '''

        service_registration_form = {
                'serviceDefinition': service.service_definition,
                'providerSystem': self.system_json,
                'serviceUri': service.service_uri,
                'interfaces': [service.interfaces],
                'secure': service.secure,
                'endOfValidity': None,
                'metadata': None,
                'version': None,
                }

        service_registration_response = requests.post(f'https://{self.sr_url}/register',
                cert=(self.certfile, self.keyfile),
                verify=False,
                json=service_registration_form)

        if service_registration_response.status_code != requests.codes.created:
            self.logger.error(f'Registration of service \'{service.service_definition}\' failed: Service Registry status {service_registration_response}')

        self.logger.info(f'Service \'{service.service_definition}\' registered in Service Registry at {service.service_uri}')

        return True
    def register_all_services(self):
        '''
        Registers all services of the system.
        '''
        for service in self.services.values():
            self.register_service(service)

    def unregister_service(self, service):
        '''
        Unregisters the given service with the service registry.

        :param service: Service to be unregistered
        :param type: ProvidedService
        '''

        unregistration_payload = {
                'service_definition': service.service_definition,
                'system_name': self.system_name,
                'address': self.address,
                'port': self.port
                }
        service_unregistration_response = requests.delete(f'https://{self.sr_url}/unregister',
                cert=(self.certfile, self.keyfile),
                verify=False,
                params=unregistration_payload)

    def unregister_all_services(self):
        '''
        Unregisters all services of the system
        '''

        for service in self.services.values():
            self.unregister_service(service)

    def run_forever(self):
        ''' Start the server, publish all service, and run until interrupted. Then, unregister all services'''

        import warnings
        warnings.simplefilter('ignore')

        self.register_all_services()
        try:
            self.logger.info(f'Starting server')
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info(f'Shutting down server')
            self.unregister_all_services()
        finally:
            self.logger.info(f'Server shut down')

    def __enter__(self):
        '''Start server and register all services'''
        import warnings
        warnings.simplefilter('ignore')

        print('Starting server')
        self.server.start()
        print('Registering services')
        self.register_all_services()

    def __exit__(self, exc_type, exc_value, tb):
        '''Unregister all services and stop the server'''
        if exc_type != KeyboardInterrupt:
            print(f'Exception was raised:')
            print(exc_value)

        print('\nSystem was stopped, unregistering services')
        self.unregister_all_services()
        print('Stopping server')
        self.server.stop()
        print('Shutdown completed')

        return True
