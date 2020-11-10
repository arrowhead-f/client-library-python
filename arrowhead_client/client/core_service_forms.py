""" Core Service Forms Module """

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Union, Sequence, Mapping

from arrowhead_client import utils
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service


class BaseServiceForm(ABC):
    """ Abstract base class for forms """

    @property
    @abstractmethod
    def dto(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        """ Compiles form into dictionary """

    def __str__(self) -> str:
        return str(self.dto)


class CoreSystemServiceForm(BaseServiceForm, ABC):
    """ Abstract base class for core system service forms """

    @property
    def dto(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        return {utils.to_camel_case(variable_name): variable for
                variable_name, variable in vars(self).items()}


@dataclass
class ServiceQueryForm(CoreSystemServiceForm):
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
class ServiceRegistrationForm(CoreSystemServiceForm):
    """ Service Registration Form """

    def __init__(
            self,
            provided_service: Service,
            provider_system: ArrowheadSystem,
            secure: str,
            metadata: Optional[Mapping[str, str]] = None,
            end_of_validity: Optional[str] = None,
            version: Optional[int] = None, ):
        self.service_definition = provided_service.service_definition
        self.service_uri = provided_service.service_uri
        self.interfaces = [provided_service.interface.dto]
        self.provider_system = provider_system.dto
        self.secure = secure
        self.metadata = metadata
        self.version = version
        self.end_of_validity = end_of_validity


class OrchestrationForm(CoreSystemServiceForm):
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
                 orchestration_flags: Optional[Mapping[str, bool]] = None, ) -> None:
        self.requester_system = requester_system
        self.requested_service = ServiceQueryForm(
                service_definition_requirement,
                interface_requirements if interface_requirements else [],
                security_requirements if security_requirements else [],
                metadata_requirements,
                version_requirement,
                max_version_requirement,
                min_version_requirement,
                ping_providers).dto
        # TODO: Implement preferred_providers
        self.preferred_providers = None
        if orchestration_flags:
            self.orchestration_flags = orchestration_flags
        else:
            self.orchestration_flags = {'overrideStore': True}
