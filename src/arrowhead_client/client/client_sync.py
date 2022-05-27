import json
from datetime import datetime
from typing import Union, Dict

from arrowhead_client import forms
from arrowhead_client import errors as errors
from arrowhead_client.constants import OrchestrationFlags
from arrowhead_client.client import core_service_responses as responses
from arrowhead_client.client.client_core import ArrowheadClient
from arrowhead_client.client.core_services import CoreServices
from arrowhead_client.rules import EventSubscriptionRule
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

        for rule in self.orchestration_rules[service_definition]:
            if not rule.active:
                continue
            try:
                return self.consumers[rule.protocol].consume_service(rule, **kwargs, )
            except OSError:
                rule.active = False
                continue

        # TODO: Not sure if this should raise an error or just log?
        raise errors.NoAvailableServicesError(
                f'No services available for'
                f' service \'{service_definition}\''
        )


    def publish_event(
            self,
            event_type: str,
            payload: Union[str, bytes, Dict],
    ):
        event_publish_form = forms.EventPublishForm(
                event_type=event_type,
                payload = str(payload if not isinstance(payload, dict) else json.dumps(payload)),
                source = self.system,
                time_stamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        event_publish_response = self.consume_service(
                CoreServices.EVENT_PUBLISH.service_definition,
                json=event_publish_form.dto(),
                cert=self.cert,
        )

        return event_publish_response


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

        self.orchestration_rules[service_definition] = rules

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
            self._initialize_event_subscription()
            self._subscribe_all_events()
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
            self._unsubscribe_all_events()
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
        # TODO: Should be a "form"?
        unregistration_payload = {
            'service_definition': service.service_definition,
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

    def _subscribe_event(self, event_rule: EventSubscriptionRule):
        event_subscription_form = forms.EventSubscribeForm(
                event_type=event_rule.event_type,
                notify_uri=event_rule.notify_uri,
                subscriber_system=event_rule.subscriber_system,
        )

        event_subscription_response = self.consume_service(
                CoreServices.EVENT_SUBSCRIBE.service_definition,
                json=event_subscription_form.dto(),
                cert=self.cert
        )

        # TODO: Process subscription response
        print(event_subscription_response)

    def _subscribe_all_events(self):
        for event_type, rule in self.event_subscription_rules.items():
            self._subscribe_event(rule)

    def _unsubscribe_event(self, rule: EventSubscriptionRule):
        unsubscription_payload = {
            "event_type": rule.event_type,
            "system_name": rule.subscriber_system.system_name,
            "address": rule.subscriber_system.address,
            "port": rule.subscriber_system.port,
        }

        event_unsubscription_response = self.consume_service(
                CoreServices.EVENT_UNSUBSCRIBE.service_definition,
                params=unsubscription_payload,
                cert=self.cert,
        )

        # TODO: Process unsubscription response
        print(event_unsubscription_response)

    def _unsubscribe_all_events(self):
        for event_type, rule in self.event_subscription_rules.items():
            self._unsubscribe_event(rule)
