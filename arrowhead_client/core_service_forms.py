#!/usr/bin/env python
''' Core Service Forms Module '''

from typing import List, Optional, Dict, Union, Any
from abc import ABC, abstractproperty
from dataclasses import dataclass
import utils


class BaseServiceForm(ABC):
    """ Abstract base class for forms """
    @abstractproperty
    def form(self):
        """ Compiles the query information into a dictionary """

    def __str__(self) -> str:
        return str(self.form)

class CoreSystemServiceForm(BaseServiceForm, ABC):
    """ Abstract base class for core system service forms """
    @property
    def form(self) -> Dict[str, Any]:
        return {utils.to_camel_case(variable_name): variable for
                variable_name, variable in vars(self).items()}

@dataclass
class ServiceQueryForm(CoreSystemServiceForm):
    ''' Service Query Form '''
    service_definition_requirement: str
    interface_requirements: Union[List[str], str]
    security_requirements: Union[List[str], str]
    metadata_requirements: Optional[Dict[str, str]] = None
    version_requirement: Optional[int] = None
    max_version_requirement: Optional[int] = None
    min_version_requirement: Optional[int] = None
    ping_providers: bool = True

    def __post_init__(self):
        self.interface_requirements = handle_requirements(self.interface_requirements)
        self.security_requirements = handle_requirements(self.security_requirements)

@dataclass
class ServiceRegistrationForm(CoreSystemServiceForm):
    ''' Service Registration Form '''
    service_definition: str
    service_uri: str
    secure: str
    interfaces: Union[List[str], str]
    provider_system: Any
    metadata: Optional[Dict[str, str]] = None
    end_of_validity: Optional[str] = None
    version: Optional[int] = None

    def __post_init__(self):
        self.interfaces = handle_requirements(self.interfaces)
        self.provider_system = self.provider_system.as_dict()

@dataclass
class OrchestrationForm(CoreSystemServiceForm):
    ''' Orchestration Form '''
    # Requester system
    requester_system: Any
    # Service requirements
    service_definition_requirement: str
    interface_requirements: Union[List[str], str, None] = None
    security_requirements: Union[List[str], str, None] = None
    metadata_requirements: Optional[Dict[str, str]] = None
    version_requirement: Optional[int] = None
    max_version_requirement: Optional[int] = None
    min_version_requirement: Optional[int] = None
    ping_providers: bool = True
    # The rest
    preferred_providers: Any = None
    orchestration_flags: Optional[Dict[str, str]] = None
    commands: Optional[Dict[str, str]] = None
    requester_cloud: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.requester_system = self.requester_system.as_dict()
        self.requested_service = ServiceQueryForm(
            self.service_definition_requirement,
            self.interface_requirements \
                    if self.interface_requirements else [],
            self.security_requirements \
                    if self.security_requirements else [],
            self.metadata_requirements,
            self.version_requirement,
            self.max_version_requirement,
            self.min_version_requirement,
            self.ping_providers).form()

        if self.orchestration_flags:
            self.orchestration_flags = self.orchestration_flags
        else:
            self.orchestration_flags = {'overrideStore': True}

if __name__ == "__main__":
    pass
