from __future__ import annotations

from typing import Any, Dict, Tuple, Callable

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.abc import BaseConsumer, BaseProvider
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.client.core_services import get_core_rules, CoreServices
from arrowhead_client.client import (
    core_service_responses as responses,
    core_service_forms as forms
)
from arrowhead_client.configuration import config as ar_config
from arrowhead_client.security.access_policy import get_access_policy
from arrowhead_client.common import Constants
from arrowhead_client.rules import (
    OrchestrationRuleContainer,
    RegistrationRule,
    OrchestrationRule,
)
import arrowhead_client.errors as errors

StoredProvidedService = Dict[str, Tuple[Service, Callable, str]]


class ArrowheadClient:
    """
    Application class for Arrowhead Systems.

    This class serves as a bridge that connects systems, consumers, and providers to the user.

    Attributes:
        system: ArrowheadSystem
        consumer: Consumer
        provider: Provider
        logger: Logger, will default to the logger found in logs.get_logger()
        keyfile: PEM keyfile
        certfile: PEM certfile
    """

    def __init__(self,
                 system: ArrowheadSystem,
                 consumer: BaseConsumer,
                 provider: BaseProvider,
                 logger: Any,
                 config: Dict = None,
                 keyfile: str = '',
                 certfile: str = '', ):
        self.system = system
        self.consumer = consumer
        self.provider = provider
        self.keyfile = keyfile
        self.certfile = certfile
        self.secure = all(self.cert)
        self._logger = logger
        self.config = config or ar_config
        self.auth_authentication_info = None
        self.orchestration_rules = OrchestrationRuleContainer()
        self._provided_services: StoredProvidedService = {}
        # TODO: Should add_provided_service be exactly the same as the provider's,
        # or should this class do something on top of it?
        # It's currently not even being used so it could likely be removed.
        # Maybe it should be it's own method?
        self.add_provided_service = self.provider.add_provided_service

    @property
    def cert(self) -> Tuple[str, str]:
        """ Tuple of the keyfile and certfile """
        return self.certfile, self.keyfile

    def setup(self):
        # Setup methods
        self._core_service_setup()

    def consume_service(self, service_definition: str, **kwargs):
        """
        Consumes the given provided_service definition

        Args:
            service_definition: The provided_service definition of a consumable provided_service
            **kwargs: Collection of keyword arguments passed to the consumer.
        """

        rule = self.orchestration_rules.get(service_definition)
        if rule is None:
            # TODO: Not sure if this should raise an error or just log?
            raise errors.NoAvailableServicesError(
                    f'No services available for'
                    f' service \'{service_definition}\''
            )

        # TODO: these should be normal arguments to consumer.consume, not a part of **kwargs
        if rule.secure == Constants.SECURITY_SECURE:
            # Add certificate files if provided_service is secure
            kwargs['cert'] = self.cert

        return self.consumer.consume_service(rule, **kwargs, )

    def add_orchestration_rule(self,
                               service_definition: str,
                               method: str,
                               access_policy: str = '',
                               # TODO: Should **kwargs just be orchestration_flags and preferred_providers?
                               **kwargs, ) -> None:
        """
        Add orchestration rule for provided_service definition

        Args:
            service_definition: Service definition that is looked up from the orchestrator.
            method: The HTTP method given in uppercase that is used to consume the provided_service.
            access_policy: Service access policy.
        """

        requested_service = Service(service_definition, access_policy=access_policy)

        orchestration_form = forms.OrchestrationForm(
                self.system,
                requested_service,
                **kwargs
        )

        orchestration_response = self.consume_service(
                CoreServices.ORCHESTRATION.service_definition,
                json=orchestration_form.dto(),
                cert=self.cert,
        )

        rules = responses.process_orchestration(orchestration_response, method)

        for rule in rules:
            self.orchestration_rules.store(rule)

    def provided_service(
            self,
            service_definition: str,
            service_uri: str,
            protocol: str,
            method: str,
            payload_format: str,
            access_policy: str,
    ) -> Callable:
        """
        Decorator to add a provided provided_service to the provider.

        Args:
            service_definition: Service definition to be stored in the provided_service registry
            service_uri: The path to the provided_service
            method: HTTP method required to access the provided_service
        """

        provided_service = Service(
                service_definition,
                service_uri,
                ServiceInterface.with_access_policy(
                        protocol,
                        access_policy,
                        payload_format,
                ),
                access_policy,
        )

        def wrapped_func(func):
            self._provided_services[service_definition] = (
                provided_service,
                func,
                method,
            )
            return func

        return wrapped_func

    def run_forever(self) -> None:
        """
        Start the server, publish all provided_service, and run until interrupted.
        Then, unregister all services.
        """

        try:
            self.setup()
            # TODO: These three should go into self.setup()
            self.auth_authentication_info = responses.process_publickey(
                    self.consume_service(CoreServices.PUBLICKEY.service_definition))
            self._initialize_provided_services()
            self._register_all_services()
            self._logger.info('Starting server')
            print('Started Arrowhead ArrowheadSystem')
            self.provider.run_forever(
                    address=self.system.address,
                    port=self.system.port,
                    # TODO: keyfile and certfile should be given in provider.__init__
                    keyfile=self.keyfile,
                    certfile=self.certfile,
            )
        except KeyboardInterrupt:
            self._logger.info('Shutting down server')
        finally:
            print('Shutting down Arrowhead system')
            self._unregister_all_services()
            self._logger.info('Server shut down')

    def _initialize_provided_services(self) -> None:
        for provided_service, func, method in self._provided_services.values():
            registration_rule = RegistrationRule(
                    provided_service,
                    provider_system=self.system,
                    method=method,
                    func=func,
                    access_policy=get_access_policy(
                            policy_name=provided_service.access_policy,
                            provided_service=provided_service,
                            privatekey=self.keyfile,
                            authorization_key=self.auth_authentication_info
                    ),
            )
            self.provider.add_provided_service(registration_rule)

    def _core_service_setup(self) -> None:
        """
        Method that sets up the test_core services.

        Runs when the client is created and should not be run manually.
        """

        core_rules = get_core_rules(self.config, self.secure)

        for rule in core_rules:
            self.orchestration_rules.store(rule)

    def _register_service(self, service: Service):
        """
        Registers the given provided_service with provided_service registry

        Args:
            service: Service to register with the Service registry.
        """

        service_registration_form = forms.ServiceRegistrationForm(
                provided_service=service,
                provider_system=self.system,
        )

        service_registration_response = self.consume_service(
                CoreServices.SERVICE_REGISTER.service_definition,
                json=service_registration_form.dto(),
                cert=self.cert
        )

        responses.process_service_register(
                service_registration_response,
        )

    def _register_all_services(self) -> None:
        """
        Registers all provided services of the system with the system registry.
        """
        for service, *_ in self._provided_services.values():
            try:
                self._register_service(service)
            except errors.CoreServiceInputError as e:
                # TODO: Do logging
                print(e)

    def _unregister_service(self, service: Service) -> None:
        """
        Unregisters the given provided_service with provided_service registry

        Args:
            service: Service to unregister with the Service registry.
        """

        service_definition = service.service_definition

        # TODO: Should be a "form"?
        unregistration_payload = {
            'service_definition': service_definition,
            'system_name': self.system.system_name,
            'address': self.system.address,
            'port': self.system.port
        }

        service_unregistration_response = self.consume_service(
                CoreServices.SERVICE_UNREGISTER.service_definition,
                params=unregistration_payload,
                cert=self.cert
        )

        responses.process_service_unregister(service_unregistration_response)

    def _unregister_all_services(self) -> None:
        """
        Unregisters all provided services of the system with the system registry.
        """

        for service, *_ in self._provided_services.values():
            try:
                self._unregister_service(service)
            except errors.CoreServiceInputError as e:
                print(e)
