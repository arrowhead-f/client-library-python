from typing import Sequence, Optional, Mapping, Union

from arrowhead_client.dto import DTOMixin
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.device import ArrowheadDevice
from arrowhead_client.common import Constants

Metadata = Mapping[str, str]
Version = Union[int, str]


####################
# SERVICE REGISTRY #
####################
class ServiceQueryForm(DTOMixin):
    """ Service Query Form """
    service_definition_requirement: str
    interface_requirements: Sequence[Optional[str]] = [None]
    security_requirements: Sequence[Optional[str]] = [None]
    metadata_requirements: Optional[Metadata] = None
    version_requirement: Optional[str] = None
    max_version_requirement: Optional[str] = None
    min_version_requirement: Optional[str] = None
    ping_providers: Optional[bool] = True

    @classmethod
    def make(
            cls,
            service: Service,
            max_version_requirement: Optional[str] = None,
            min_version_requirement: Optional[str] = None,
            ping_providers: Optional[bool] = True
    ) -> 'ServiceQueryForm':
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


class ServiceDefinitionResponse(DTOMixin):
    id: int
    service_definition: str
    created_at: str
    updated_at: str


class ServiceProviderResponse(DTOMixin):
    id: int
    system_name: str
    address: str
    port: str
    authentication_info: str
    created_at: str
    updated_at: str


class ServiceInterfaceResponse(DTOMixin):
    id: int
    interface_name: str
    created_at: str
    updated_at: str


class ServiceRegistryEntry(DTOMixin):
    id: int
    service_definition: ServiceDefinitionResponse
    provider: ServiceProviderResponse
    service_uri: str
    end_of_validity: str = None
    metadata: Metadata = None
    version: int = None
    interfaces: Sequence[ServiceInterfaceResponse] = None
    created_at: str = None
    updated_at: str = None


class ServiceQueryResponse(DTOMixin):
    service_query_data: Sequence[ServiceRegistryEntry]
    unfiltered_hits: int


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
                service_definition=provided_service.service_definition,
                service_uri=provided_service.service_uri,
                interfaces=[provided_service.interface.dto()],
                provider_system=provider_system,
                secure=provided_service.access_policy,
                metadata=provided_service.metadata,
                version=provided_service.version,
                end_of_validity=end_of_validity,
        )
        # TODO: How to do end_of_validity?


################
# ORCHESTRATOR #
################
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
                ),
                orchestration_flags=orchestration_flags or default_flags,
                preferred_providers=preferred_providers,
        )


class OrchestrationResponse(DTOMixin):
    provider: ServiceProviderResponse
    service: ServiceDefinitionResponse
    service_uri: str
    secure: str
    metadata: Optional[Metadata] = None
    interfaces: Sequence[ServiceInterfaceResponse] = None
    version: Version = None
    authorization_tokens: Mapping[str, str] = None
    warnings: Sequence[str] = None


class OrchestrationResponseList(DTOMixin):
    response: Sequence[OrchestrationResponse]


################
# EVENTHANDLER #
################

class EventPublishForm(DTOMixin):
    event_type: str
    meta_data: Mapping[str, str]
    payload: str
    source: ArrowheadSystem
    time_stamp: str


class EventSubscribeForm(DTOMixin):
    event_type: str
    filter_meta_data: Mapping[str, str]
    match_meta_data: bool
    notify_uri: str
    sources: Sequence[ArrowheadSystem]
    start_date: str
    end_date: str
    subscriber_system: ArrowheadSystem


##################
# SYSTEMREGISTRY #
##################

class SystemQueryForm(DTOMixin):
    device_name_requirements: str
    system_name_requirements: str
    metadata_requirements: Mapping[str, str]
    version_requirement: Union[int, str]
    max_version_requirement: Union[int, str]
    min_version_requirement: Union[int, str]
    ping_providers: bool


class SystemRegisterForm(DTOMixin):
    system: ArrowheadSystem
    provider: ArrowheadDevice
    metadata: Mapping[str, str]
    version: Union[int, str]
    end_of_validity: str


##################
# DEVICEREGISTRY #
##################

class DeviceQueryForm(DTOMixin):
    address_requirement: str
    device_name_requirements: str
    mac_address_requirement: str
    metadata_requirements: Mapping[str, str]
    version_requirement: Union[int, str]
    max_version_requirement: Union[int, str]
    min_version_requirement: Union[int, str]


class DeviceRegisterForm(DTOMixin):
    device: ArrowheadDevice
    metadata: Mapping[str, str]
    version: Union[int, str]
    end_of_validity: str


##############
# ONBOARDING #
##############

class OnboardingCsrForm(DTOMixin):
    # TODO: This is probably a special kind of string
    certificate_signing_request: str


class OnboardingNameForm(DTOMixin):
    device_name: str


########################
# CERTIFICATEAUTHORITY #
########################

class CertificateCheckForm(DTOMixin):
    version: int = 1
    certificate: str
