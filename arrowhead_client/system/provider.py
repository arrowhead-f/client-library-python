from functools import partial
from typing import Optional, Callable
from flask import Flask, request
from gevent import pywsgi # type: ignore
from arrowhead_client.core_service_forms import ServiceRegistrationForm
from arrowhead_client.service import ProvidedHttpService
from arrowhead_client.core_services import core_service
from arrowhead_client.system.consumer import ConsumerSystem


class ProviderSystem(ConsumerSystem):
    """ Class for service provision """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = Flask(__name__)
        # Add logging handlers for flask (DOES NOT WORK CURRENTLY)
        for handler in self.logger.handlers:
            self.app.logger.addHandler(handler)
        self.provided_services = {}
        self.server = pywsgi.WSGIServer((self.address, int(self.port)), self.app,
                                        keyfile=self.keyfile, certfile=self.certfile,
                                        log=self.logger)
        self._provider_core_system_setup()

    def _provider_core_system_setup(self) -> None:
        self._consumed_services['register'] = core_service('register')
        self._consumed_services['unregister'] = core_service('unregister')

    def add_provided_service(self,
                             service_definition: str = '',
                             service_uri: str = '',
                             interface: str = '',
                             http_method: str = '',
                             address: str = '',
                             port: str = '',
                             provided_service: ProvidedHttpService = None,
                             provides: Optional[Callable] = None) -> None:
        """ Add service to provider system"""

        if not provided_service:
            provided_service = ProvidedHttpService(
                    service_definition,
                    service_uri,
                    interface,
                    address,
                    port,
                    http_method,
                    provides)

        if provided_service.service_definition not in self.provided_services:
            # Register service with Flask app
            self.provided_services[provided_service.service_definition] = provided_service
            if provided_service.http_method != 'GET' and callable(provided_service.provides):
                # If HTTP method is POST, add request object to view_func
                provided_service.provides = partial(provided_service.provides, request)
            self.app.add_url_rule(rule=f'/{provided_service.service_uri}',
                                  endpoint=provided_service.service_definition,
                                  methods=[provided_service.http_method],
                                  view_func=provided_service.provides)
        else:
            # TODO: Add log message when service is trying to be overwritten
            pass

    def provided_service(self,
                         service_definition: str,
                         service_uri: str,
                         interface: str,
                         method: str,
                         address: str = '',
                         port: str = '',) -> Callable:
        """ Decorator to add provided services """
        def wrapped_func(func):
            self.add_provided_service(
                    service_definition,
                    service_uri,
                    interface,
                    method,
                    address,
                    port,
                    provides=func)
            return func
        return wrapped_func

    def register_service(self, service_definition: str):
        """ Registers the given service with service registry """

        service = self.provided_services[service_definition]

        service_registration_form = ServiceRegistrationForm(
                service_definition=service.service_definition,
                service_uri=service.service_uri,
                secure='CERTIFICATE',
                # TODO: secure should _NOT_ be hardcoded
                interfaces=service.interface.dto,
                provider_system=self.dto
        )

        service_registration_response = self.consume_service(
                'register',
                json=service_registration_form.dto,
        )
        #TODO: Error handling

        # TODO: Fix the logging
        """
        if service_registration_response.status_code != requests.codes.created:
            self.logger.error(
                f'Registration of service \'{service.service_definition}\' failed: Service Registry status {service_registration_response}')

        self.logger.info(
            f'Service \'{service.service_definition}\' registered in Service Registry at {service.service_uri}')
        """

        return True

    def register_all_services(self):
        """ Registers all services of the system. """
        for service in self.provided_services.values():
            self.register_service(service.service_definition)

    def unregister_service(self, service_definition):
        """ Unregisters the given service with the service registry. """

        unregistration_payload = {
            'service_definition': service_definition,
            'system_name': self.system_name,
            'address': self.address,
            'port': self.port
        }

        service_unregistration_response = self._consumed_services['unregister'].consume(
                cert=self.cert,
                params=unregistration_payload
        )

    def unregister_all_services(self):
        """ Unregisters all services of the system """

        for service_definition in self.provided_services:
            self.unregister_service(service_definition)

    def run_forever(self):
        """ Start the server, publish all service, and run until interrupted. Then, unregister all services"""

        import warnings
        warnings.simplefilter('ignore')

        self.register_all_services()
        try:
            self.logger.info(f'Starting server')
            print('Started Arrowhead System')
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info(f'Shutting down server')
            print('Shutting down Arrowhead system')
            self.unregister_all_services()
        finally:
            self.logger.info(f'Server shut down')

    """
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
    """
