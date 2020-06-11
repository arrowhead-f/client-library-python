from __future__ import annotations

import configparser
from typing import Any, Dict, Tuple
from gevent import pywsgi # type: ignore
from arrowhead_client.system import ArrowheadSystem
#from arrowhead_client.consumer import Consumer
from arrowhead_client.abc import BaseConsumer
from arrowhead_client.provider import Provider
from arrowhead_client.service import Service
from arrowhead_client.client.core_services import core_service
from arrowhead_client.client import core_service_forms as forms, core_service_responses as responses


class ArrowheadClient():
    """
    Application class for Arrowhead Systems.

    This class serves as a bridge that connects systems, consumers, and providers to the user.

    Args:
        system: ArrowheadSystem
        consumer: Consumer
        provider: Provider
        logger: Logger, will default to the logger found in logs.get_logger()
        config: JSON config file containing the addresses and ports of the core systems
        server: WSGI server
        keyfile: PEM keyfile
        certfile: PEM certfile
    """
    def __init__(self,
                 system: ArrowheadSystem,
                 consumer: BaseConsumer,
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


    @classmethod
    def from_cfg(cls, properties_file: str) -> ArrowheadClient:
        """ Creates a BaseArrowheadSystem from a descriptor file """
        raise NotImplementedError

        # Parse configuration file
        config = configparser.ConfigParser()
        with open(properties_file, 'r') as properties:
            config.read_file(properties)
        config_dict = {k: v for k, v in config.items('APPLICATION')}

        # TODO: Extract information and create class instance

        # Create class instance
        arrowhead_application = cls(**config_dict)

        return arrowhead_application

    def consume_service(self, service_definition: str, **kwargs):
        """
        Consumes the given service definition

        Args:
            service_definition: The service definition of a consumable service
            **kwargs: Collection of keyword arguments passed to the consumer.
        """
        return self.consumer.consume_service(service_definition, **kwargs)

    def add_consumed_service(self,
                             service_definition: str,
                             http_method: str) -> None:
        """
        Add orchestration rule for service definition

        Args:
            service_definition: Service definition that is looked up from the orchestrator.
            http_method: The HTTP method given in uppercase that is used to consume the service.
        """

        orchestration_form = forms.OrchestrationForm(self.system.dto, service_definition)

        orchestration_response = self.consume_service('orchestration-service',
                                                      json=orchestration_form.dto,
                                                      cert=self.cert,
                                                      )
        #TODO: Handle orchestrator error codes

        orchestration_payload = orchestration_response.json() # This might change with backend

        (orchestrated_service, system), *_ = responses.handle_orchestration_response(orchestration_payload)

        #TODO: Handle response with more than 1 service
        # Perhaps a list of consumed services for each service definition should be stored
        self._store_consumed_service(orchestrated_service, system, http_method)

    def provided_service(
            self,
            service_definition: str,
            service_uri: str,
            interface: str,
            method: str,
            *func_args,
            **func_kwargs,):
        """
        Decorator to add a provided service to the provider.

        Args:
            service_definition: Service definition to be stored in the service registry
            service_uri: The path to the service
            interface: Arrowhead interface string(s)
            method: HTTP method required to access the service
        """
        service = Service(
                service_definition,
                service_uri,
                interface,
        )
        def wrapped_func(func):
            self.provider.add_provided_service(
                    service,
                    http_method=method,
                    view_func=func,
                    *func_args,
                    **func_kwargs)
            return func
        return wrapped_func

    def run_forever(self) -> None:
        """ Start the server, publish all service, and run until interrupted. Then, unregister all services"""

        import warnings
        warnings.simplefilter('ignore')

        self._register_all_services()
        try:
            self._logger.info(f'Starting server')
            print('Started Arrowhead ArrowheadSystem')
            self.server.serve_forever()
        except KeyboardInterrupt:
            self._logger.info(f'Shutting down server')
            print('Shutting down Arrowhead system')
            self._unregister_all_services()
        finally:
            self._logger.info(f'Server shut down')

    @property
    def cert(self) -> Tuple[str, str]:
        """
        Tuple of the keyfile and certfile
        """
        return self.certfile, self.keyfile

    def _core_system_setup(self) -> None:
        """
        Method that sets up the core services.

        It is run when the client is created and should not be run manually.
        """
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

        self._store_consumed_service(core_service('register'), service_registry, 'POST')
        self._store_consumed_service(core_service('unregister'), service_registry, 'DELETE')
        self._store_consumed_service(core_service('orchestration-service'), orchestrator, 'POST')

    def _store_consumed_service(
            self,
            service: Service,
            system: ArrowheadSystem,
            http_method: str) -> None:
        """
        Register consumed services with the consumer

        Args:
            service: Service to be stored
            system: System containing the service
            http_method: HTTP method used to consume the service
        """

        self.consumer._consumed_services[service.service_definition] = (service, system, http_method)


    def _register_service(self, service: Service):
        """
        Registers the given service with service registry

        Args:
            service: Service to register with the Service registry.
        """

        # TODO: Should accept a system and a service
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
                cert=self.cert
        )

        print(service_registration_response.status_code)
        # TODO: Error handling

        # TODO: Do logging


    def _register_all_services(self) -> None:
        """
        Registers all provided services of the system with the system registry.
        """
        for service, _ in self.provider.provided_services.values():
            self._register_service(service)


    def _unregister_service(self, service_definition: str) -> None:
        """
        Unregisters the given service with service registry

        Args:
            service: Service to unregister with the Service registry.
        """

        if service_definition not in self.provider.provided_services.keys():
            raise ValueError(f'{service_definition} not provided by {self}')

        # TODO: Should be a "form"?
        unregistration_payload = {
            'service_definition': service_definition,
            'system_name': self.system.system_name,
            'address': self.system.address,
            'port': self.system.port
        }

        service_unregistration_response = self.consume_service(
                'unregister',
                params=unregistration_payload,
                cert=self.cert
        )

        print(service_unregistration_response.status_code)


    def _unregister_all_services(self) -> None:
        """
        Unregisters all provided services of the system with the system registry.
        """

        for service_definition in self.provider.provided_services:
            self._unregister_service(service_definition)




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

        print('\nArrowheadSystem was stopped, unregistering services')
        self.unregister_all_services()
        print('Stopping server')
        self.server.stop()
        print('Shutdown completed')

        return True
    """
if __name__ == '__main__':
    pass
