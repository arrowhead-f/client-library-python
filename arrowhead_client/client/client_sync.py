from typing import Optional
import warnings

import arrowhead_client.client.core_service_forms.client as forms
from arrowhead_client import errors as errors
from arrowhead_client.constants import OrchestrationFlags
from arrowhead_client.client import core_service_responses as responses
from arrowhead_client.client.client_core import ArrowheadClient
from arrowhead_client.client.core_services import CoreServices
from arrowhead_client.service import Service, ServiceInterface

class ArrowheadClientSync(ArrowheadClient):
    """
    Base class for asynchronous Arrowhead Clients.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def consume_service(
            self,
            service_definition: str,
            **kwargs
    ):
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

        return self.consumer.consume_service(rule, **kwargs, )

    def add_orchestration_rule(
            self,
            service_definition: str,
            method: str,
            protocol: str = '',
            access_policy: str = '',
            payload_format: str = '',
            # TODO: Should **kwargs just be orchestration_flags and preferred_providers?
            orchestration_flags: OrchestrationFlags = OrchestrationFlags.OVERRIDE_STORE,
            **kwargs,
    ) -> None:
        """
        Add orchestration rule for provided_service definition

        Args:
            service_definition: Service definition that is looked up from the orchestrator.
            method: The HTTP method given in uppercase that is used to consume the provided_service.
            access_policy: Service access policy.
        """

        requested_service = Service(
                service_definition,
                interface=ServiceInterface.with_access_policy(
                        protocol,
                        access_policy,
                        payload_format,
                ),
                access_policy=access_policy
        )

        orchestration_form = forms.OrchestrationForm.make(
                self.system,
                requested_service,
                orchestration_flags,
                **kwargs
        )

        # TODO: Add an argument for arrowhead forms in consume_service, and one for the ssl-files
        orchestration_response = self.consume_service(
                CoreServices.ORCHESTRATION.service_definition,
                json=orchestration_form.dto(),
                cert=self.cert,
        )

        rules = responses.process_orchestration(orchestration_response, method)

        for rule in rules:
            self.orchestration_rules.store(rule)

    def run_forever(self) -> None:
        """
        Start the server, publish all provided_service, and run until interrupted.
        Then, unregister all services.
        """

        try:
            self.setup()
            # TODO: These three could go into a provider_setup() method
            if self.secure:
                authorization_response = self.consume_service(CoreServices.PUBLICKEY.service_definition)
                self.auth_authentication_info = responses.process_publickey(authorization_response)
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

    def _register_service(self, service: Service):
        """
        Registers the given provided_service with provided_service registry

        Args:
            service: Service to register with the Service registry.
        """

        service_registration_form = forms.ServiceRegistrationForm.make(
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
        for rule in self.registration_rules:
            try:
                self._register_service(rule.provided_service)
            except errors.CoreServiceInputError as e:
                # TODO: Do logging
                print(e)
            else:
                rule.is_provided = True

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

        for rule in self.registration_rules:
            if not rule.is_provided:
                continue
            try:
                self._unregister_service(rule.provided_service)
            except errors.CoreServiceInputError as e:
                print(e)
            else:
                rule.is_provided = False
