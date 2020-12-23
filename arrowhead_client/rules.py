from dataclasses import dataclass
from typing import Optional, Iterator, Callable, Dict
from collections.abc import MutableMapping

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service
from arrowhead_client.security.access_policy import AccessPolicy


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
    def metadata(self) -> Optional[Dict]:
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


# TODO: Give this class the same treatment as OrchestrationRule
# I.e. give it bunch of properties to decouple the behaviours of systems/services and providers
class RegistrationRule:
    def __init__(
            self,
            provided_service: Service,
            provider_system: ArrowheadSystem,
            method: str,
            func: Callable,
            access_policy: AccessPolicy = None,
    ):
        self._provided_service = provided_service
        self._provider_system = provider_system
        self._method = method
        self._func = func
        self._access_policy = access_policy
        self.is_provided = False

    @property
    def service_definition(self):
        return self._provided_service.service_definition

    @property
    def service_uri(self):
        return self._provided_service.service_uri

    @property
    def provided_service(self):
        return self._provided_service

    @property
    def authority(self):
        return self._provider_system.authority

    @property
    def method(self):
        return self._method

    @property
    def func(self):
        return self._func

    @property
    def access_policy(self):
        return self._access_policy

    @access_policy.setter
    def access_policy(self, new_policy: AccessPolicy):
        self._access_policy = new_policy

    def is_authorized(self, consumer_cert_str: str, auth_str: str):
        return self._access_policy.is_authorized(consumer_cert_str, auth_str)


class OrchestrationRuleContainer(MutableMapping):
    def __init__(self):
        self._rulecontainer = {}

    def __getitem__(self, key: str) -> OrchestrationRule:
        return self._rulecontainer[key]

    def __setitem__(
            self,
            key: str,
            item: OrchestrationRule
            ) -> None:
        self._rulecontainer[key] = item

    def __delitem__(self, key: str) -> None:
        del self._rulecontainer[key]

    def __iter__(self) -> Iterator[OrchestrationRule]:
        return iter(self._rulecontainer)

    def __len__(self) -> int:
        return len(self._rulecontainer)

    def store(self, item: OrchestrationRule) -> None:
        self[item.service_definition] = item


class RegistrationRuleContainer:
    def __init__(self):
        self._rulecontainer = {}

    def __iter__(self) -> Iterator[RegistrationRule]:
        return iter(self._rulecontainer.values())

    def __len__(self):
        return len(self._rulecontainer)

    def store(self, item: RegistrationRule):
        self._rulecontainer[item.service_definition] = item

    def retrieve(self, service_definition: str):
        return self._rulecontainer[service_definition]