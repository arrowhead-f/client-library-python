from collections import namedtuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

ProvidedService = namedtuple('ProvidedService', 
        ['service_definition', 'service_uri', 'interfaces', 'secure', 'service_function'])

@dataclass
class ProviderSystem:
    system_name: str
    address: str
    port: int
    authenticationInfo: str

    @classmethod
    def from_csr(cls, csr_system):
        ''' Creates a ProviderSystem from system description in core service response '''
        system_name = csr_system['systemName']
        address = csr_system['address']
        port = csr_system['port']
        authentication_info = csr_system['authenticationInfo']
        return cls(system_name, address, port, authentication_info)

"""
@dataclass
class ProvidedService(ABC):
    service_definition: str
    service_uri: str
    interfaces: str
    secure: str

    @abstractmethod
    def service_function(self):
        pass
"""

@dataclass
class ConsumedService:
    service_definition: str
    service_uri: str
    interface: str
    secure: str
    provider_system: ProviderSystem

    @classmethod
    def from_orch_response(cls, orch_response):
        provider_system = ProviderSystem.from_csr(orch_response['provider'])
        args = [orch_response['service']['serviceDefinition'],
                orch_response['serviceUri'],
                orch_response['interfaces'],
                orch_response['secure'],
                provider_system]

        return cls(*args)

    @property
    def url(self):
        system_url = f'{self.provider_system.address}:{self.provider_system.port}'
        return f'https://{system_url}{self.service_uri}'

if __name__ == '__main__':
    sys_a = ProviderSystem('test_system', '127.0.0.1', 1543, '')
    a = ConsumedService('test', '/test', 'HTTP-SECURE-JSON', 'CERTIFICATE', sys_a)
