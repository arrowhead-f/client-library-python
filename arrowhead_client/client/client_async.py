from arrowhead_client import errors as errors
from arrowhead_client.client import core_service_responses as responses, core_service_forms as forms
from arrowhead_client.client.client_core import ArrowheadClientBase
from arrowhead_client.client.core_services import CoreServices
from arrowhead_client.service import Service, ServiceInterface


class ArrowheadClientAsync(ArrowheadClientBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def consume_service(self, service_definition, **kwargs):
        rule = self.orchestration_rules.get(service_definition)
        if rule is None:
            # TODO: Not sure if this should raise an error or just log?
            raise errors.NoAvailableServicesError(
                    f'No services available for'
                    f' service \'{service_definition}\''
            )

        return await self.consumer.consume_service(rule, **kwargs)

    async def setup(self):
        super().setup()

        await self.consumer.async_startup()

    async def add_orchestration_rule(
            self,
            service_definition: str,
            method: str,
            protocol: str = '',
            access_policy: str = '',
            format: str = '',
            # TODO: Should **kwargs just be orchestration_flags and preferred_providers?
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
                        format,
                ),
                access_policy=access_policy
        )

        orchestration_form = forms.OrchestrationForm.make(
                self.system,
                requested_service,
                **kwargs
        )

        # TODO: Add an argument for arrowhead forms in consume_service, and one for the ssl-files
        orchestration_response = await self.consume_service(
                CoreServices.ORCHESTRATION.service_definition,
                json=orchestration_form.dto(),
                #cert=self.cert,
        )

        rules = responses.process_orchestration(orchestration_response, method)

        for rule in rules:
            self.orchestration_rules.store(rule)

    async def _register_service(self, service: Service):
        service_registration_form = forms.ServiceRegistrationForm.make(
                provided_service=service,
                provider_system=self.system,
        )

        service_registration_response = await self.consume_service(
                CoreServices.SERVICE_REGISTER.service_definition,
                json=service_registration_form.dto(),
                cert=self.cert
        )

        responses.process_service_register(service_registration_response)

    async def _register_all_services(self):
        for rule in self.registration_rules:
            try:
                await self._register_service(rule.provided_service)
            except errors.CoreServiceInputError as e:
                # TODO: Do logging
                print(e)
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
                cert=self.cert
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

    async def run_forever(self):
        pass

    async def __aenter__(self):
        await self.setup()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.consumer.async_shutdown()
