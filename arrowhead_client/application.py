from __future__ import annotations
from typing import Any, Dict
from gevent import pywsgi # type: ignore
from arrowhead_client.consumer import Consumer
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.provider import Provider
from arrowhead_client.service import Service
from arrowhead_client.core_services import core_service
from arrowhead_client.system import ArrowheadSystem
import arrowhead_client.core_service_forms as forms



class ArrowheadApplication():
    def __init__(self,
                 system: ArrowheadSystem,
                 consumer: Consumer,
                 provider: Provider,
                 logger: Any,
                 config: Dict,
                 server: Any = None,  # type: ignore
                 keyfile: str = '',
                 certfile: str  = '', ):
        self.system = system
        self.consumer = consumer
        self.provider = provider
        self._logger = logger
        self.keyfile = keyfile
        self.certfile = certfile
        self.config = config
        #TODO: Remove this hardcodedness
        self.server = pywsgi.WSGIServer((self.system.address, self.system.port), self.provider.app,
                                        keyfile=self.keyfile, certfile=self.certfile,
                                        log=self._logger)
        self._core_system_setup()
        self.add_provided_service = self.provider.add_provided_service

    '''
    @classmethod
    def from_cfg(cls, properties_file: str) -> ArrowheadApplication:
        """ Creates a BaseArrowheadSystem from a descriptor file """

        # Parse configuration file
        config = configparser.ConfigParser()
        with open(properties_file, 'r') as properties:
            config.read_file(properties)
        config_dict = {k: v for k, v in config.items('SYSTEM')}

        # Create class instance
        system = cls(**config_dict)

        return system
    '''

    def _core_system_setup(self) -> None:
        service_registry = ArrowheadSystem(
                'service_registry',
                str(self.config['service_registry']['address']),
                int(self.config['service_registry']['port']),
                ''
        )
        orchestrator = ArrowheadSystem(
                'orchestrator',
                str(self.config['orchestrator']['address']),
                int(self.config['orchestrator']['port']),
                '')

        self.consumer._register_consumed_service(core_service('register'), service_registry, 'POST')
        self.consumer._register_consumed_service(core_service('unregister'), service_registry, 'DELETE')
        self.consumer._register_consumed_service(core_service('orchestration-service'), orchestrator, 'POST')

    def consume_service(self, service_definition: str, **kwargs):
        return self.consumer.consume_service(service_definition, **kwargs)

    def _register_service(self, service: Service):
        """ Registers the given service with service registry """

        service_registration_form = forms.ServiceRegistrationForm(
                service_definition=service.service_definition,
                service_uri=service.service_uri,
                secure='CERTIFICATE',
                # TODO: secure should _NOT_ be hardcoded
                interfaces=service.interface.dto,
                provider_system=self.system.dto
        )

        service_registration_response = self.consume_service(
                'register',
                json=service_registration_form.dto,
        )
        # TODO: Error handling

        # TODO: Do logging

        return True

    def provided_service(self,
                         service_definition: str,
                         service_uri: str,
                         interface: str,
                         method: str):
        def wrapped_func(func):
            self.provider.add_provided_service(
                    service_definition,
                    service_uri,
                    interface,
                    http_method=method,
                    view_func=func)
            return func
        return wrapped_func

    def _register_all_services(self) -> None:
        """ Registers all services of the system. """
        for service, _ in self.provider.provided_services.values():
            self._register_service(service)


    def _unregister_service(self, service_definition: str) -> None:
        """ Unregisters the given service with the service registry. """

        if service_definition not in self.provider.provided_services.keys():
            raise ValueError(f'{service_definition} not provided by {self}')

        unregistration_payload = {
            'service_definition': service_definition,
            'system_name': self.system.system_name,
            'address': self.system.address,
            'port': self.system.port
        }

        service_unregistration_response = self.consume_service(
                'unregister',
                params=unregistration_payload
        )


    def _unregister_all_services(self) -> None:
        """ Unregisters all services of the system """

        for service_definition in self.provider.provided_services:
            self._unregister_service(service_definition)


    def run_forever(self) -> None:
        """ Start the server, publish all service, and run until interrupted. Then, unregister all services"""

        import warnings
        warnings.simplefilter('ignore')

        self._register_all_services()
        try:
            self._logger.info(f'Starting server')
            print('Started Arrowhead System')
            self.server.serve_forever()
        except KeyboardInterrupt:
            self._logger.info(f'Shutting down server')
            print('Shutting down Arrowhead system')
            self._unregister_all_services()
        finally:
            self._logger.info(f'Server shut down')


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
if __name__ == '__main__':
    pass
