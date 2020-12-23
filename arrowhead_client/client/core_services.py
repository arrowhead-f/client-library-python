from typing import Dict
from enum import Enum

from arrowhead_client.service import Service


class CoreServiceConfig(str, Enum):
    CORE_SERVICE_SERVICE_REGISTRY_REGISTER = 'register'
    CORE_SERVICE_SERVICE_REGISTRY_UNREGISTER = 'unregister'
    SERVICE_REGISTRY_REGISTER_URI = 'serviceregistry/register'
    SERVICE_REGISTRY_REGISTER_METHOD = 'POST'
    SERVICE_REGISTRY_UNREGISTER_URI = 'serviceregistry/unregister'
    SERVICE_REGISTRY_UNREGISTER_METHOD = 'DELETE'

_http_core_services: Dict[str, Service] = {
    'register': Service(
            service_definition='register',
            service_uri='serviceregistry/register',
            interface='HTTP-SECURE-JSON', ),
    'query': Service(
            service_definition='query',
            service_uri='serviceregistry/query',
            interface='HTTP-SECURE-JSON', ),
    'unregister': Service(
            service_definition='unregister',
            service_uri='serviceregistry/unregister',
            interface='HTTP-SECURE-TEXT', ),
    'orchestration-provided_service': Service(
            service_definition='orchestration-provided_service',
            service_uri='orchestrator/orchestration',
            interface='HTTP-SECURE-JSON', ),
    'publickey': Service(
            service_definition='publickey',
            service_uri='authorization/publickey',
            interface='HTTP-SECURE-JSON', ),
}


def core_service(service_defintion: str) -> Service:
    core_service_instance = _http_core_services.get(service_defintion, None)

    if not core_service_instance:
        raise ValueError(f'Core provided_service \'{service_defintion}\' not found, '
                         f'available core services are {list(_http_core_services.keys())}')

    return core_service_instance
