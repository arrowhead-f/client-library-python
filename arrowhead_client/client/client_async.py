import json
from datetime import datetime
from typing import Dict, Union
import arrowhead_client.client.core_service_forms.client
from arrowhead_client import errors as errors
from arrowhead_client.client import core_service_responses as responses
from arrowhead_client.client.client_core import ArrowheadClient
from arrowhead_client.client.core_services import CoreServices
from arrowhead_client.rules import EventSubscriptionRule
from arrowhead_client.service import Service
from arrowhead_client.provider.implementations.fastapi_provider import FastapiProvider
from arrowhead_client.response import Response, ConnectionResponse
from arrowhead_client.constants import OrchestrationFlags
from arrowhead_client.client.core_service_forms import client as forms


class ArrowheadClientAsync(ArrowheadClient):
    """
    Base class for asynchronous Arrowhead Clients.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider.add_startup_routine(self.client_setup)
        self.provider.add_shutdown_routine(self.client_cleanup)

    async def consume_service(self, service_definition, **kwargs) -> Response:
        rule = self.orchestration_rules.get(service_definition)
        if rule is None:
            # TODO: Not sure if this should raise an error or just log?
            raise errors.NoAvailableServicesError(
                    f'No services available for'
                    f' service \'{service_definition}\''
            )
        res = await self.consumers[rule.protocol].consume_service(rule, **kwargs)  # type: ignore
        return res

    async def publish_event(
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
        event_publish_response = await self.consume_service(
                CoreServices.EVENT_PUBLISH.service_definition,
                json=event_publish_form.dto(),
                cert=self.cert,
        )

        return event_publish_response

    async def connect(self, service_definition, **kwargs) -> ConnectionResponse:
        rule = self.orchestration_rules.get(service_definition)
        if rule is None:
            # TODO: Not sure if this should raise an error or just log?
            raise errors.NoAvailableServicesError(
                    f'No services available for'
                    f' service \'{service_definition}\''
            )

        connector = await self.consumers[rule.protocol].connect(rule, **kwargs)

        return connector

    async def setup(self):
        super().setup()

        for consumer in self.consumers.values():
            await consumer.async_startup()

    async def add_orchestration_rule(  # type: ignore
            self,
            service_definition: str,
            method: str,
            protocol: str = '',
            access_policy: str = '',
            payload_format: str = '',
            orchestration_flags: OrchestrationFlags = OrchestrationFlags.OVERRIDE_STORE,
            **kwargs,
    ):
        """
        Add orchestration rule for provided_service definition

        Args:
            service_definition: Service definition that is looked up from the orchestrator.
            method: The HTTP method given in uppercase that is used to consume the provided_service.
            access_policy: Service access policy.
        """

        requested_service = Service.make(
                service_definition,
                protocol=protocol,
                access_policy=access_policy,
                payload_format=payload_format,
        )

        orchestration_form = arrowhead_client.client.core_service_forms.client.OrchestrationForm.make(
                self.system,
                requested_service,
                orchestration_flags,
                **kwargs
        )

        # TODO: Add an argument for arrowhead forms in consume_service, and one for the ssl-files
        orchestration_response = await self.consume_service(
                CoreServices.ORCHESTRATION.service_definition,
                json=orchestration_form.dto(),
                # cert=self.cert,
        )

        rules = responses.process_orchestration(orchestration_response, method)

        for rule in rules:
            self.orchestration_rules.store(rule)

    async def _register_service(self, service: Service):
        service_registration_form = arrowhead_client.client.core_service_forms.client.ServiceRegistrationForm.make(
                provided_service=service,
                provider_system=self.system,
        )

        service_registration_response = await self.consume_service(
                CoreServices.SERVICE_REGISTER.service_definition,
                json=service_registration_form.dto(),
        )

        responses.process_service_register(service_registration_response)

    async def _register_all_services(self):
        for rule in self.registration_rules:
            if rule.is_provided:
                continue
            try:
                await self._register_service(rule.provided_service)
            except errors.CoreServiceInputError as e:
                # TODO: logging
                if str(e).endswith('already exists.'):
                    rule.is_provided = True
            else:
                rule.is_provided = True

    async def _unregister_service(self, service: Service):
        unregistration_payload = {
            'service_definition': service.service_definition,
            'system_name': self.system.system_name,
            'address': self.system.address,
            'port': self.system.port,
        }

        service_unregistration_response = await self.consume_service(
                CoreServices.SERVICE_UNREGISTER.service_definition,
                params=unregistration_payload,
        )

        responses.process_service_unregister(service_unregistration_response)

    async def _unregister_all_services(self):
        for rule in self.registration_rules:
            if not rule.is_provided:
                continue
            try:
                await self._unregister_service(rule.provided_service)
            except errors.CoreServiceInputError as e:
                print(e)
            else:
                rule.is_provided = False

    async def _subscribe_event(self, event_rule: EventSubscriptionRule):
        event_subscription_form = forms.EventSubscribeForm(
                event_type=event_rule.event_type,
                notify_uri=event_rule.notify_uri,
                subscriber_system=event_rule.subscriber_system,
        )

        event_subscription_response = await self.consume_service(
                CoreServices.EVENT_SUBSCRIBE.service_definition,
                json=event_subscription_form.dto(),
        )

        # TODO: Process subscription response
        print(event_subscription_response)

    async def _subscribe_all_events(self):
        for event_type, rule in self.event_subscription_rules.items():
            await self._subscribe_event(rule)

    async def _unsubscribe_event(self, rule: EventSubscriptionRule):
        unsubscription_payload = {
            "event_type": rule.event_type,
            "system_name": rule.subscriber_system.system_name,
            "address": rule.subscriber_system.address,
            "port": rule.subscriber_system.port,
        }

        event_unsubscription_response = await self.consume_service(
                CoreServices.EVENT_UNSUBSCRIBE.service_definition,
                params=unsubscription_payload,
        )

        # TODO: Process unsubscription response
        print(event_unsubscription_response)

    async def _unsubscribe_all_events(self):
        for event_type, rule in self.event_subscription_rules.items():
            await self._unsubscribe_event(rule)

    def run_forever(self):
        self.provider.run_forever(
                address=self.system.address,
                port=self.system.port,
                # TODO: keyfile and certfile should be given in provider.__init__
                keyfile=self.keyfile,
                certfile=self.certfile,
        )

    async def client_setup(self):
        await self.setup()
        if self.secure:
            authorization_response = await self.consume_service(CoreServices.PUBLICKEY.service_definition)
            self.auth_authentication_info = responses.process_publickey(authorization_response)
        self._initialize_provided_services()
        await self._register_all_services()
        self._initialize_event_subscription()
        await self._subscribe_all_events()

    async def client_cleanup(self):
        print('Shutting down Arrowhead Client')
        await self._unregister_all_services()
        await self._unsubscribe_all_events()
        for consumer in self.consumers:
            await consumer.async_shutdown()
        self._logger.info('Server shut down')

    async def __aenter__(self):
        await self.setup()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for consumer in self.consumers.values():
            await consumer.async_shutdown()
