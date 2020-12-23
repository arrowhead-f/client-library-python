""" Core Service Forms Module """

from dataclasses import dataclass
from typing import Optional, Union, Sequence, Mapping, List

from arrowhead_client.dto import DTOMixin
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service


@dataclass
class ServiceQueryForm(DTOMixin):
    """ Service Query Form """
    service_definition_requirement: str
    interface_requirements: Sequence[str]
    security_requirements: Sequence[str]
    metadata_requirements: Optional[Mapping[str, str]] = None
    version_requirement: Optional[int] = None
    max_version_requirement: Optional[int] = None
    min_version_requirement: Optional[int] = None
    ping_providers: bool = True

    @classmethod
    def make(cls,
             service: Service,
             max_version_requirement: Optional[int] = None,
             min_version_requirement: Optional[int] = None,
             ping_providers: bool = True) -> 'ServiceQueryForm':
        return cls(
                service.service_definition,
                [service.interface.dto()] if service.interface else [''],
                [service.access_policy],
                service.metadata,
                service.version,
                max_version_requirement,
                min_version_requirement,
                ping_providers,
        )


class ServiceRegistrationForm(DTOMixin):
    """ Service Registration Form """

    def __init__(
            self,
            provided_service: Service,
            provider_system: ArrowheadSystem,
            end_of_validity: Optional[str] = None, ):
        self.service_definition = provided_service.service_definition
        self.service_uri = provided_service.service_uri
        self.interfaces = [provided_service.interface.dto()]
        self.provider_system = provider_system.dto()
        self.secure = provided_service.access_policy
        self.metadata = provided_service.metadata
        self.version = provided_service.version
        self.end_of_validity = end_of_validity
        # TODO: How to do end_of_validity?


# TODO: Let this class use boolean operators?
@dataclass
class OrchestrationFlags(DTOMixin):
    matchmaking: bool = False
    metadata_search: bool = False
    only_preferred: bool = False
    ping_providers: bool = False
    override_store: bool = True
    enable_inter_cloud: bool = False
    trigger_inter_cloud: bool = False

    @property
    def _dto_excludes(self):
        return {var for var, val in vars(self).items() if not val}


class OrchestrationForm(DTOMixin):
    """ Orchestration Form """

    def __init__(self,
                 requester_system: ArrowheadSystem,
                 requested_service: Service,
                 orchestration_flags: OrchestrationFlags = None, ) -> None:
        self.requester_system = requester_system.dto(exclude={'authentication_info'})
        self.requested_service = ServiceQueryForm.make(
                requested_service,
        ).dto(exclude={'ping_providers'})
        # TODO: Implement preferred_providers
        self.preferred_providers = None
        self.orchestration_flags = orchestration_flags.dto() \
            if orchestration_flags else OrchestrationFlags().dto()
