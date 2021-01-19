""" Core Service Forms Module """

from typing import Optional, Sequence, Mapping

from arrowhead_client.dto import DTOMixin
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service


class ServiceQueryForm(DTOMixin):
    """ Service Query Form """
    service_definition_requirement: str
    interface_requirements: Sequence[Optional[str]] = [None]
    security_requirements: Sequence[Optional[str]] = [None]
    metadata_requirements: Optional[Mapping[str, str]] = None
    version_requirement: Optional[str] = None
    max_version_requirement: Optional[str] = None
    min_version_requirement: Optional[str] = None
    ping_providers: Optional[bool] = True

    @classmethod
    def make(cls,
             service: Service,
             max_version_requirement: Optional[str] = None,
             min_version_requirement: Optional[str] = None,
             ping_providers: Optional[bool] = True) -> 'ServiceQueryForm':

        return cls(
                service_definition_requirement=service.service_definition,
                interface_requirements=[service.interface.dto() if service.interface else None],
                security_requirements=[service.access_policy or None],
                metadata_requirements=service.metadata,
                version_requirement=service.version,
                max_version_requirement=max_version_requirement,
                min_version_requirement=min_version_requirement,
                ping_providers=ping_providers,
        )


class ServiceRegistrationForm(DTOMixin):
    """ Service Registration Form """
    service_definition: str
    service_uri: str
    interfaces: Sequence[str] = [None]
    provider_system: ArrowheadSystem
    secure: str = ''
    metadata: Mapping = None
    version: Optional[str] = None
    end_of_validity: str = None

    @classmethod
    def make(
            # TODO: add more options that overrides the values in provided_service
            cls,
            provided_service: Service,
            provider_system: ArrowheadSystem,
            end_of_validity: Optional[str] = None,
    ):

        return cls(
                service_definition = provided_service.service_definition,
                service_uri = provided_service.service_uri,
                interfaces = [provided_service.interface.dto()],
                provider_system = provider_system,
                secure = provided_service.access_policy,
                metadata = provided_service.metadata,
                version = provided_service.version,
                end_of_validity = end_of_validity,
        )
                # TODO: How to do end_of_validity?


# TODO: Let this class use boolean operators?
class OrchestrationFlags(DTOMixin):
    matchmaking: bool = False
    metadata_search: bool = False
    only_preferred: bool = False
    ping_providers: bool = False
    override_store: bool = False
    enable_inter_cloud: bool = False
    trigger_inter_cloud: bool = False

default_flags = OrchestrationFlags(override_store=True)

class OrchestrationForm(DTOMixin):
    """ Orchestration Form """
    requester_system: ArrowheadSystem
    requested_service: ServiceQueryForm
    orchestration_flags: OrchestrationFlags
    preferred_providers: Optional[Mapping] = None

    @classmethod
    def make(
            cls,
            requester_system: ArrowheadSystem,
            requested_service: Service,
            orchestration_flags: OrchestrationFlags = None,
            preferred_providers: Mapping = None,
    ):

        return cls(
                requester_system=requester_system,
                requested_service=ServiceQueryForm.make(
                        requested_service,
                        ping_providers=None
                ),
                orchestration_flags=orchestration_flags or default_flags,
                preferred_providers=preferred_providers,
        )
