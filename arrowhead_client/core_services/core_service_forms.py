""" Core Service Forms Module """

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Union, Sequence, Mapping

from arrowhead_client.mixins import DTOMixin
from arrowhead_client import utils
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service


# TODO: This class is unnecessary now, should be removed
class BaseServiceForm(ABC):
    """ Abstract base class for forms """

    @property
    @abstractmethod
    def dto(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        """ Compiles form into dictionary """

    def __str__(self) -> str:
        return str(self.dto)


@dataclass
class ServiceQueryForm(DTOMixin):
    """ Service Query Form """
    service_definition_requirement: str
    interface_requirements: Union[Sequence[str], str]
    security_requirements: Union[Sequence[str], str]
    metadata_requirements: Optional[Mapping[str, str]] = None
    version_requirement: Optional[int] = None
    max_version_requirement: Optional[int] = None
    min_version_requirement: Optional[int] = None
    ping_providers: bool = True

    def __post_init__(self):
        self.interface_requirements = utils.uppercase_strings_in_list(self.interface_requirements)
        self.security_requirements = utils.uppercase_strings_in_list(self.security_requirements)


@dataclass
class ServiceRegistrationForm(DTOMixin):
    """ Service Registration Form """

    def __init__(
            self,
            provided_service: Service,
            provider_system: ArrowheadSystem,
            end_of_validity: Optional[str] = None, ):
        self.service_definition = provided_service.service_definition
        self.service_uri = provided_service.service_uri
        self.interfaces = [provided_service.interface.dto]
        self.provider_system = provider_system.dto
        self.secure = provided_service.access_policy
        self.metadata = provided_service.metadata
        self.version = provided_service.version
        self.end_of_validity = end_of_validity
        # TODO: How to do end_of_validity

@dataclass
class OrchestrationFlags(DTOMixin):
    matchmaking: bool = False
    metadata_search: bool = False
    only_preferred: bool = False
    ping_providers: bool = False
    override_store: bool = True
    enable_inter_cloud: bool = False
    trigger_inter_cloud: bool = False

    # TODO: Handle case where flag is not bool?


class OrchestrationForm(DTOMixin):
    """ Orchestration Form """

    def __init__(self,
                 requester_system: BaseServiceForm,
                 service_definition_requirement: str,
                 interface_requirements: Union[Sequence[str], str] = None,
                 security_requirements: Optional[Union[Sequence[str], str]] = None,
                 metadata_requirements: Optional[Mapping[str, str]] = None,
                 version_requirement: Optional[int] = None,
                 max_version_requirement: Optional[int] = None,
                 min_version_requirement: Optional[int] = None,
                 ping_providers: bool = True,
                 orchestration_flags: Optional[OrchestrationFlags] = None, ) -> None:
        self.requester_system = requester_system
        # TODO: Change `... if ... else []` to `... or []`, test later if it works
        self.requested_service = ServiceQueryForm(
            service_definition_requirement,
            interface_requirements or [],
            security_requirements or [],
            metadata_requirements,
            version_requirement,
            max_version_requirement,
            min_version_requirement,
            ping_providers).dto
        # TODO: Implement preferred_providers
        self.preferred_providers = None
        self.orchestration_flags = orchestration_flags.dto or {'overrideStore': True}
        # TODO: If line above works, remove the commented code below
        """
        if orchestration_flags:
            self.orchestration_flags = orchestration_flags
        else:
            self.orchestration_flags = {'overrideStore': True}
        """