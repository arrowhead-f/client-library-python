from __future__ import annotations

from typing import Any, Dict, Tuple, Callable, Union
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.abc import BaseConsumer, BaseProvider
from arrowhead_client.service import Service
from arrowhead_client.client.core_services import core_service
from arrowhead_client.client import core_service_forms as forms, core_service_responses as responses

StoredConsumedService = Dict[str, Tuple[Service, ArrowheadSystem, str]]
StoredProvidedService = Dict[str, Tuple[Service, Callable]]


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
                 provider: BaseProvider,
                 logger: Any,
                 config: Dict,
                 keyfile: str = '',
                 certfile: str = '', ):
        self.system = system
        self.consumer = consumer
        self.provider = provider
        self._logger = logger
        self.keyfile = keyfile
        self.certfile = certfile
        self.secure = True if self.keyfile else False
        self.config = config
        self._consumed_services: StoredConsumedService = {}
        self._provided_services: StoredProvidedService = {}

        # Setup methods
        self._core_system_setup()
        self.add_provided_service = self.provider.add_provided_service

    def consume_service(self, service_definition: str, **kwargs):
        """
        Consumes the given service definition

        Args:
            service_definition: The service definition of a consumable service
            **kwargs: Collection of keyword arguments passed to the consumer.
        """
        consumed_service, consumer_system, method = self._consumed_services[service_definition]

        service_uri = _service_uri(consumed_service, consumer_system)

        if consumed_service.interface.secure == 'SECURE':
            # Add certificate files if service is secure
            kwargs['cert'] = self.cert

        return self.consumer.consume_service(service_uri, method, **kwargs)

    def extract_payload(self, service_response: Any, payload_type: str) -> Union[Dict, str]:
        return self.consumer.extract_payload(service_response, payload_type)

    def add_consumed_service(self,
                             service_definition: str,
                             method: str,
                             **kwargs, ) -> None:
        """
        Add orchestration rule for service definition

        Args:
            service_definition: Service definition that is looked up from the orchestrator.
            method: The HTTP method given in uppercase that is used to consume the service.
        """

        orchestration_form = forms.OrchestrationForm(
                self.system.dto,
                service_definition,
                **kwargs
        )

        orchestration_response = self.consume_service(
                'orchestration-service',
                json=orchestration_form.dto,
                cert=self.cert,
        )

        # TODO: Handle orchestrator error codes

        orchestration_payload = self.consumer.extract_payload(
                orchestration_response,
                'json'
        )

        (orchestrated_service, system), *_ = responses.handle_orchestration_response(orchestration_payload)

        # TODO: Handle response with more than 1 service
        # Perhaps a list of consumed services for each service definition should be stored
        self._store_consumed_service(orchestrated_service, system, method)

    def provided_service(
            self,
            service_definition: str,
            service_uri: str,
            interface: str,
            method: str,
            *func_args,
            **func_kwargs, ):
        """
        Decorator to add a provided service to the provider.

        Args:
            service_definition: Service definition to be stored in the service registry
            service_uri: The path to the service
            interface: Arrowhead interface string(s)
            method: HTTP method required to access the service
        """
        provided_service = Service(
                service_definition,
                service_uri,
                interface,
        )

        def wrapped_func(func):
            self._provided_services[service_definition] = (provided_service, func)
            self.provider.add_provided_service(
                    service_definition,
                    service_uri,
                    method=method,
                    func=func,
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
            self._logger.info('Starting server')
            print('Started Arrowhead ArrowheadSystem')
            self.provider.run_forever()
        except KeyboardInterrupt:
            self._logger.info('Shutting down server')
            print('Shutting down Arrowhead system')
            self._unregister_all_services()
        finally:
            self._logger.info('Server shut down')

    @property
    def cert(self) -> Tuple[str, str]:
        """
        Tuple of the keyfile and certfile
        """
        return self.certfile, self.keyfile

    def _core_system_setup(self) -> None:
        """
        Method that sets up the core services.

        Runs when the client is created and should not be run manually.
        """

        self._store_consumed_service(
                core_service('register'),
                self.config['service_registry'],
                'POST')
        self._store_consumed_service(
                core_service('unregister'),
                self.config['service_registry'],
                'DELETE')
        self._store_consumed_service(
                core_service('orchestration-service'),
                self.config['orchestrator'],
                'POST')

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

        self._consumed_services[service.service_definition] = (service, system, http_method)

    def _register_service(self, service: Service):
        """
        Registers the given service with service registry

        Args:
            service: Service to register with the Service registry.
        """

        # Decide security level:
        if service.interface.secure == 'INSECURE':
            secure = 'NOT_SECURE'
        elif service.interface.secure == 'SECURE':
            secure = 'CERTIFICATE'
        else:
            secure = 'CERTIFICATE'
        # TODO: Add 'TOKEN' security level

        # TODO: Should accept a system and a service
        service_registration_form = forms.ServiceRegistrationForm(
                provided_service=service,
                provider_system=self.system,
                # TODO: secure should _NOT_ be hardcoded
                secure=secure
        )

        service_registration_response = self.consume_service(
                'register',
                json=service_registration_form.dto,
                cert=self.cert
        )

        print(service_registration_response.status_code)
        print(service_registration_response.text)
        # TODO: Error handling

        # TODO: Do logging

    def _register_all_services(self) -> None:
        """
        Registers all provided services of the system with the system registry.
        """
        for service, _ in self._provided_services.values():
            self._register_service(service)

    def _unregister_service(self, service_definition: str) -> None:
        """
        Unregisters the given service with service registry

        Args:
            service: Service to unregister with the Service registry.
        """

        if service_definition not in self._provided_services.keys():
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

        for service_definition in self._provided_services:
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


def _service_uri(service: Service, system: ArrowheadSystem) -> str:
    service_uri = f'{system.authority}/{service.service_uri}'

    return service_uri
