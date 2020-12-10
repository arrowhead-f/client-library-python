from dataclasses import dataclass
from typing import Optional, Iterator, Union, Tuple, Callable, Dict
from collections.abc import MutableMapping

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.security.access_policy import AccessPolicy

# TODO: The OrchestrationRuleTuple should be removed eventually
OrchestrationRuleTuple = Tuple[Service, ArrowheadSystem, str, str]


class OrchestrationRule:
    def __init__(
            self,
            consumed_service: Service,
            provider_system: ArrowheadSystem,
            method: str,
            authorization_token: str = '',
        ):
        self._consumed_service = consumed_service
        self._provider_system = provider_system
        self._method = method
        self._authorization_token = authorization_token

    @property
    def service_definition(self) -> str:
        return self._consumed_service.service_definition

    @property
    def protocol(self) -> str:
        return self._consumed_service.interface.protocol

    @property
    def secure(self) -> str:
        return self._consumed_service.interface.secure

    @property
    def payload_type(self) -> str:
        return self._consumed_service.interface.payload

    @property
    def access_policy(self) -> str:
        return self._consumed_service.access_policy

    @property
    def metadata(self) -> Dict:
        return self._consumed_service.metadata

    @property
    def version(self) -> Optional[int]:
        return self._consumed_service.version

    @property
    def system_name(self) -> str:
        return self._provider_system.system_name

    @property
    def endpoint(self) -> str:
        return f'{self._provider_system.address}:' \
               f'{self._provider_system.port}/' \
               f'{self._consumed_service.service_uri}'

    @property
    def authentication_info(self) -> str:
        return self._provider_system.authentication_info

    @property
    def method(self) -> str:
        return self._method

    @property
    def authorization_token(self) -> str:
        return self._authorization_token


@dataclass
class ProvisionRule:
    provided_service: Service
    provider_system: ArrowheadSystem
    method: str
    func: Callable
    access_policy: Optional[AccessPolicy]


class OrchestrationRuleContainer(MutableMapping):
    def __init__(self):
        self._rulecontainer = {}

    def __getitem__(self, key: str) -> OrchestrationRule:
        return self._rulecontainer[key]

    def __setitem__(
            self,
            key: str,
            item: Union[OrchestrationRule, OrchestrationRuleTuple]) -> None:
        if isinstance(item, OrchestrationRule):
            self._rulecontainer[key] = item
        else:
            # If given a tuple of values, create the orchestrationrule
            # TODO: This is not necessary and will be removed in the future, connected to comment at the top
            self._rulecontainer[key] = OrchestrationRule(*item)

    def __delitem__(self, key: str) -> None:
        del self._rulecontainer[key]

    def __iter__(self) -> Iterator:
        return iter(self._rulecontainer)

    def __len__(self) -> int:
        return len(self._rulecontainer)

    def store(self, item: OrchestrationRule) -> None:
        self[item.service_definition] = item
