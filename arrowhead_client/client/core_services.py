from typing import Dict, List
from enum import Enum
from collections import namedtuple

from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.common import Constants

CoreConfig = namedtuple(
        'CoreConfig',
        ['service_definition',
         'uri',
         'method',
         'protocol',
         'payload',
         'system',
         ]
)

class CoreServices(CoreConfig, Enum):
    # Core services
    SERVICE_REGISTER = (
        'service-register',
        'serviceregistry/register',
        'POST', 'HTTP', 'JSON',
        'service_registry',
    )
    SERVICE_UNREGISTER = (
        'service-unregister',
        'serviceregistry/unregister',
        'DELETE', 'HTTP', 'JSON',
        'service_registry',
    )
    SERVICE_QUERY = (
        'service-query',
        'serviceregistry/query',
        'POST', 'HTTP', 'JSON',
        'service_registry',
    )
    ORCHESTRATION = (
        'orchestration-service',
        'orchestrator/orchestration',
        'POST', 'HTTP', 'JSON',
        'orchestrator',
    )
    PUBLICKEY = (
        'auth-public-key',
        'authorization/publickey',
        'GET', 'HTTP', 'JSON',
        'authorization',
    )

def get_core_rules(config: Dict, secure: bool) -> List[OrchestrationRule]:
    # TODO: Turn this loop into comprehension?
    rules = []
    for core_service in CoreServices:
        secure = Constants.SECURITY_SECURE if secure else Constants.SECURITY_INSECURE
        access_policy = Constants.POLICY_CERTIFICATE if secure else Constants.POLICY_UNRESTRICTED
        rules.append(
                OrchestrationRule(
                        Service(
                                core_service.service_definition,
                                core_service.uri,
                                ServiceInterface(
                                        core_service.protocol,
                                        secure,
                                        core_service.payload
                                ),
                                access_policy,
                        ),
                        config['core_service'][core_service.system],
                        core_service.method,
                )
        )

    return rules
