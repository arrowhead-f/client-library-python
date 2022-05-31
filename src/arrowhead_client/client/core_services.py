from __future__ import annotations

from typing import Dict, List, Tuple
from enum import Enum
from collections import namedtuple
from typing import Mapping, cast

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client import constants, forms

CoreConfig = namedtuple(
    "CoreConfig",
    [
        "service_definition",
        "uri",
        "method",
        "protocol",
        "payload",
        "system",
        "data_model"
    ],
)


class CoreServices(CoreConfig, Enum):
    # Core services
    SERVICE_REGISTER = (
        "service-register",
        "serviceregistry/register",
        "POST",
        "HTTP",
        "JSON",
        constants.CoreSystem.SERVICE_REGISTRY.value,
        forms.ServiceRegistrationForm,
    )
    SERVICE_UNREGISTER = (
        "service-unregister",
        "serviceregistry/unregister",
        "DELETE",
        "HTTP",
        "JSON",
        constants.CoreSystem.SERVICE_REGISTRY.value,
        None,
    )
    SERVICE_QUERY = (
        "service-query",
        "serviceregistry/query",
        "POST",
        "HTTP",
        "JSON",
        constants.CoreSystem.SERVICE_REGISTRY.value,
        forms.ServiceQueryForm,
    )
    ORCHESTRATION = (
        "orchestration-service",
        "orchestrator/orchestration",
        "POST",
        "HTTP",
        "JSON",
        constants.CoreSystem.ORCHESTRATOR.value,
        forms.OrchestrationForm,
    )
    PUBLICKEY = (
        "auth-public-key",
        "authorization/publickey",
        "GET",
        "HTTP",
        "JSON",
        constants.CoreSystem.AUTHORIZATION.value,
        None,
    )
    EVENT_PUBLISH = (
        "event-publish",
        "eventhandler/publish",
        "POST",
        "HTTP",
        "JSON",
        constants.CoreSystem.EVENT_HANDLER.value,
        forms.EventPublishForm,
    )
    EVENT_SUBSCRIBE = (
        "event-subscribe",
        "eventhandler/subscribe",
        "POST",
        "HTTP",
        "JSON",
        constants.CoreSystem.EVENT_HANDLER.value,
        forms.EventSubscribeForm,
    )
    EVENT_UNSUBSCRIBE = (
        "event-unsubscribe",
        "eventhandler/unsubscribe",
        "DELETE",
        "HTTP",
        "JSON",
        constants.CoreSystem.EVENT_HANDLER.value,
        None,
    )


def get_core_rules(config: Mapping, secure: bool) -> List[OrchestrationRule]:
    """
    Get orchestration rules for core services.

    Args:
        config: Configuration dictionary.
        secure: True if ssl is enabled, False otherwise.
    Returns:
        List of Orchestration rules.
    """

    rules: List[OrchestrationRule] = [
        cast(OrchestrationRule, _extract_rule(core_service, config, secure))
        for core_service in CoreServices
        if _extract_rule(core_service, config, secure) is not None
    ]

    return rules


def _extract_rule(
    core_service_tuple: CoreConfig, config: Mapping, secure: bool
) -> OrchestrationRule | None:
    secure_string = constants.Security.SECURE if secure else constants.Security.INSECURE
    access_policy = (
        constants.AccessPolicy.CERTIFICATE
        if secure
        else constants.AccessPolicy.UNRESTRICTED
    )
    interface = ServiceInterface(
        core_service_tuple.protocol, secure_string, core_service_tuple.payload
    )
    try:
        core_system = ArrowheadSystem(**config[core_service_tuple.system])
    except KeyError:
        return None
    return OrchestrationRule(
        Service(
            core_service_tuple.service_definition,
            core_service_tuple.uri,
            interface,
            access_policy,
        ),
        core_system,
        core_service_tuple.method,
        data_model = core_service_tuple.data_model,
    )
