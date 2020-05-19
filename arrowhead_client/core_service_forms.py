#!/usr/bin/env python
""" Core Service Forms Module """

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Union, Any, Sequence, Mapping

from . import utils
from .utils import ServiceInterface


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
        self.interface_requirements = utils.handle_requirements(self.interface_requirements)
        self.security_requirements = utils.handle_requirements(self.security_requirements)


@dataclass
class ServiceRegistrationForm(CoreSystemServiceForm):
    """ Service Registration Form """
    service_definition: str
    service_uri: str
    secure: str
    interfaces: Union[Sequence[str], str]
    provider_system: BaseServiceForm
    metadata: Optional[Mapping[str, str]] = None
    end_of_validity: Optional[str] = None
    version: Optional[int] = None

    def __post_init__(self):
        self.interfaces = [self.interfaces]

class OrchestrationForm(CoreSystemServiceForm):
    """ Orchestration Form """

    def __init__(self,
                 requester_system: BaseServiceForm,
                 service_definition_requirement: str,
                 interface_requirements: Optional[Union[Sequence[str], str]] = None,
                 security_requirements: Optional[Union[Sequence[str], str]] = None,
                 metadata_requirements: Optional[Mapping[str, str]] = None,
                 version_requirement: Optional[int] = None,
                 max_version_requirement: Optional[int] = None,
                 min_version_requirement: Optional[int] = None,
                 ping_providers: bool = True,
                 orchestration_flags: Optional[Mapping[str, bool]] = None,
                 commands: Optional[Mapping[str, str]] = None,
                 requester_cloud: Optional[Mapping[str, Union[str, bool, Sequence[int]]]] = None) -> None:
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
        self.commands = commands
        self.requester_cloud = requester_cloud

        if orchestration_flags:
            self.orchestration_flags = orchestration_flags
        else:
            self.orchestration_flags = {'overrideStore': True}


if __name__ == "__main__":
    pass
