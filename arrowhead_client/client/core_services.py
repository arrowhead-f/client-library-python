from typing import Dict
from copy import deepcopy
from arrowhead_client.service import Service

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
    'orchestration-service': Service(
            service_definition='orchestration-service',
            service_uri='orchestrator/orchestration',
            interface='HTTP-SECURE-JSON', )
}


def core_service(service_defintion: str) -> Service:
    core_service_instance = deepcopy(_http_core_services.get(service_defintion, None))

    if not core_service_instance:
        raise ValueError(f'Core service \'{service_defintion}\' not found, '
                         f'available core services are {list(_http_core_services.keys())}')

    return core_service_instance
