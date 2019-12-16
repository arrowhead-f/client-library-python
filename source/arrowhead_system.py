from dataclasses import dataclass, field, asdict
from flask import Flask, url_for, request
from gevent import pywsgi
import requests
import requests_pkcs12
from pprint import pprint
from collections import namedtuple
from functools import wraps
from time import sleep

def parse_service_query_response(service_query_response, num_responses=1):
    service_query_data = service_query_response.json()['serviceQueryData']

    if not service_query_data:
        return []
    if num_responses == 1:
        return service_query_data[0]
    elif num_responses > 1:
        return service_query_data[0:num_responses]
    else:
        raise ValueError("Number of requested responses must be larger than 0")

ArrowheadService = namedtuple('ArrowheadService', 
        ['service_definition', 'service_uri', 'interfaces', 'secure', 'service_function'])

class ArrowheadSystem():
    '''
    Arrowhead System class.
    :param system_name: Name of the system
    :type system_name: str
    :param address: IP-address of the system (IPv4)
    :type address: str
    :param port: Port of the system
    :type port: str
    :param authentication_info: Authentication info for token security, not implented yet
    :type authentication_info: str
    :param sr_address: Local cloud service registry address
    :type sr_address: str
    :param sr_port: Local cloud service registry port
    :type sr_port: str
    :param keyfile: Location of tls keyfile
    :type keyfile: str
    :param certfile: Location of tls certfile
    :type certfile: str
    '''
    def __init__(self, system_name, address, port, authentication_info, sr_address, sr_port,
            keyfile, certfile):
        self.system_name = system_name
        self.address = address
        self.port = port
        self.authentication_info = authentication_info
        self.sr_address = sr_address
        self.sr_port = sr_port
        self.keyfile = keyfile
        self.certfile = certfile
        self.orch_address, self.orch_port = self._get_orch_url()
        self.app = Flask(__name__)#self.setup_app()
        self.services = {}
        self.setup_echo()
        self.server = pywsgi.WSGIServer((self.address, int(self.port)), self.app,
                keyfile=self.keyfile, certfile=self.certfile)

    def add_service(self, service_definition, service_uri, interfaces, secure='CERTIFICATE'):
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
            raise ValueError('CERTIFICATE is currently the only supported security')

        def decorator(f):
            self.services[service_definition] = ArrowheadService(
                    service_definition, service_uri, interfaces, secure, f)
            self.app.add_url_rule(service_uri, service_definition, f)

            return f

        return decorator

    def setup_echo(self):
        @self.add_service('echo', '/echo', 'HTTP-SECURE-JSON')
        def echo():
            return 'Got it!'

    def setup_app(self):
        '''
        Creates the wsgi app used by the system for service provision

        :returns: The created wsgi app
        :rtype: wsgi app
        '''
        app = Flask(__name__)

        @app.route('/echo')
        def echo():
            return 'Got it!'

        return app

    def register_service(self, service):
        '''
        Registers the given service with service registry

        :param service: Service to be registered
        :param type: ArrowheadService
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
        pprint(service_registration_form)
        service_registration_response = requests.post(f'https://{self.sr_url}/register',
                cert=(self.certfile, self.keyfile),
                verify=False,
                json=service_registration_form)
        print(service_registration_response.text)

    def register_all_services(self):
        '''
        Registers all services of the system.
        '''
        for service in self.services.values():
            test_system.register_service(service)

    def unregister_service(self, service):
        '''
        Unregisters the given service with the service registry.

        :param service: Service to be unregistered
        :param type: ArrowheadService
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
            test_system.unregister_service(service)

    @property
    def sr_url(self):
        '''
        Creates the service registry url given the address and port.

        :returns: Service registry url
        :rtype: str
        '''

        return f'{self.sr_address}:{self.sr_port}/serviceregistry'

    @property
    def orch_url(self):
        '''
        Creates the orchestrator url given the address and port.

        :returns: Orchestrator url
        :rtype: str
        '''

        return f'{self.orch_address}:{self.orch_port}/orchestration'

    @property
    def system_json(self):
        '''
        Creates a dictionary of the ArrowheadSystem to be used in various forms.

        :returns: Representation of ArrowheadSystem
        :rtype: dict
        '''

        return {
            "systemName": self.system_name,
            "address": self.address,
            "port": int(self.port),
            "authenticationInfo": self.authentication_info
            }

    def _verify_sr(self):
        '''
        Verifies that the connection to the service registry is established.

        :returns: Verification of connection
        :rtype: bool
        :raises: :class:`RuntimeError`: Connection not established
        '''

        r = requests.get(f'https://{self.sr_url}/echo',
                cert=(self.certfile, self.keyfile),
                verify=False)
        if r.status_code >= 200 and r.status_code < 300:
            return True
        else:
            raise RuntimeError(f'Service registry error response <{r.status_code}>')

    def query_sr(self, 
            service_definition_requirement,
            interface_requirements,
            security_requirements):
        '''
        Queries the service registry for a service

        :param service_definition_requirement: Requested service definition
        :type service_definition_requirement: str
        :param interface_requirements: Requested service interfaces
        :type interface_requirements: str
        :param security_requirements: Requested service security
        :type security_requirements: str

        :returns: service query response
        :rtype: dict
        '''
        service_query_form = {
                "serviceDefinitionRequirement": service_definition_requirement,
                "interfaceRequirements": [interface_requirements.upper()],
                "securityRequirements": [security_requirements.upper()],
                "metadataRequirements": None,
                "versionRequirement": None,
                "maxVersionRequirement": None,
                "minVersionRequirement": None,
                "pingProviders": True
                }

        service_query_response = requests.post(f'https://{self.sr_url}/query',
                cert=(self.certfile, self.keyfile),
                verify=False,
                json=service_query_form)

        return service_query_response

    def query_orchestration(self):
        orchestration_form = {
                "commands": {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string"
                    },
                "orchestrationFlags": {
                    "additionalProp1": True,
                    "additionalProp2": True,
                    "additionalProp3": True
                    },
                "preferredProviders": [
                    {
                        "providerCloud": {
                            "authenticationInfo": "string",
                            "gatekeeperRelayIds": [
                                0
                                ],
                            "gatewayRelayIds": [
                                0
                                ],
                            "name": "string",
                            "neighbor": True,
                            "operator": "string",
                            "secure": True
                            },
                        "providerSystem": {
                            "address": "string",
                            "authenticationInfo": "string",
                            "port": 0,
                            "systemName": "string"
                            }
                        }
                    ],
                "requestedService": {
                    "interfaceRequirements": [
                        "string"
                        ],
                    "maxVersionRequirement": 0,
                    "metadataRequirements": {
                        "additionalProp1": "string",
                        "additionalProp2": "string",
                        "additionalProp3": "string"
                        },
                    "minVersionRequirement": 0,
                    "pingProviders": True,
                    "securityRequirements": [
                        "NOT_SECURE"
                        ],
                    "serviceDefinitionRequirement": "string",
                    "versionRequirement": 0
                    },
                "requesterCloud": {
                        "authenticationInfo": "string",
                        "gatekeeperRelayIds": [
                            0
                            ],
                        "gatewayRelayIds": [
                            0
                            ],
                        "name": "string",
                        "neighbor": True,
                        "operator": "string",
                        "secure": True
                        },
                "requesterSystem": {
                        "address": "string",
                        "authenticationInfo": "string",
                        "port": 0,
                        "systemName": "string"
                        }
                }

    def _get_orch_url(self):
        '''
        Request the orchestration service from the service registry

        :returns: Orchestrator address and port
        :rtype: tuple
        '''

        if not self._verify_sr():
            return False

        service_query_response = self.query_sr('orchestration-service',
                'HTTP-SECURE-JSON',
                'CERTIFICATE')

        orchestrator_data = parse_service_query_response(service_query_response, 1)

        orch_address = orchestrator_data['provider']['address']
        if orch_address == 'orchestrator':
            orch_address = self.sr_address
        orch_port = orchestrator_data['provider']['port']

        return orch_address, orch_port

    def run_forever(self):
        ''' Start the server, publish all service, and run until interrupted. Then, unregister all services'''

        import warnings
        warnings.simplefilter('ignore')

        self.register_all_services()
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down server')
            self.unregister_all_services()
        finally:
            print('Server shut down')

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
            print(f'Exception was raised')
        print('\nSystem was stopped, unregistering services')
        self.unregister_all_services()
        print('Stopping server')
        self.server.stop()
        print('Shutdown completed')

        return True

if __name__ == '__main__':
    test_system = ArrowheadSystem('time_provider', 'localhost', '1337', '', '127.0.0.1', '8443',
            'certificates/time_provider.key', 'certificates/time_provider.crt')

    #test_system.add_service('test', '/test/test', 'HTTP-SECURE-JSON')
    #print(test_system.services)
    #print(test_system._verify_sr())
    @test_system.add_service('test', '/test/test', 'HTTP-SECURE-JSON')
    def test():
        return 'test'

    #test_system.run_forever()
    with test_system as system:
        while True:
            sleep(1)

