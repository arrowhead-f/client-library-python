"""
============
Rules Module
============
"""
from typing import Optional, Iterator, Callable, Dict
from collections.abc import MutableMapping

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service
from arrowhead_client.security.access_policy import AccessPolicy
from arrowhead_client import errors
from arrowhead_client.types import Version, Metadata


class OrchestrationRule:
    """
    Collection of objects necessary to perform service consumption.
    """

    def __init__(
            self,
            consumed_service: Service,
            provider_system: ArrowheadSystem,
            method: str = '',
            authorization_token: str = '',
    ):
        """
        Args:
            consumed_service: Service to be consumed.
            provider_system: System providing service.
            method: What method, if the protocol requires one, is used to consume the service.
            authorization_token: Authorization token provided by the :ref:`authorization-system` if consumed service uses the token access policy.
        """
        self._consumed_service = consumed_service
        self._provider_system = provider_system
        self._method = method
        self._authorization_token = authorization_token

    @property
    def service_definition(self) -> str:
        """Service definition registered in the :ref:`service-registry`"""
        return self._consumed_service.service_definition

    @property
    def protocol(self) -> str:
        """Protocol (e.g. ``HTTP`` or ``WS``)"""
        return self._consumed_service.interface.protocol

    @property
    def secure(self) -> str:
        """Security level, either ``SECURE`` (tls) or ``NOT_SECURE`` (no tls)"""
        return self._consumed_service.interface.secure

    @property
    def payload_type(self) -> str:
        """Payload type, e.g. ``JSON`` or ``TEXT``"""
        return self._consumed_service.interface.payload

    @property
    def access_policy(self) -> str:
        """Access policy used by consumed service, either ``TOKEN``, ``CERTIFICATE``, or ``UNRESTRICTED``"""
        return self._consumed_service.access_policy

    @property
    def metadata(self) -> Optional[Metadata]:
        """Metadata registered in the :ref:`service-registry`"""
        return self._consumed_service.metadata

    @property
    def version(self) -> Optional[Version]:
        """Version of consumed service"""
        return self._consumed_service.version

    @property
    def system_name(self) -> str:
        """Provider system name"""
        return self._provider_system.system_name

    @property
    def endpoint(self) -> str:
        """The URI to the service, without the protocol"""
        return f'{self._provider_system.address}:' \
               f'{self._provider_system.port}/' \
               f'{self._consumed_service.service_uri}'

    @property
    def authentication_info(self) -> str:
        """Provider system certificate string in DER format"""
        return self._provider_system.authentication_info

    @property
    def method(self) -> str:
        """Method used by service"""
        return self._method

    @property
    def authorization_token(self) -> str:
        """Authorization token"""
        return self._authorization_token


# TODO: Give this class the same treatment as OrchestrationRule
# I.e. give it bunch of properties to decouple the behaviours of systems/services and providers
class RegistrationRule:
    """
    Collection of objects necessary to provide a service.
    """

    def __init__(
            self,
            provided_service: Service,
            provider_system: ArrowheadSystem,
            method: str,
            func: Callable,
            access_policy: AccessPolicy = None,
    ):
        """
            provided_service: Service provided by the ``provider_system``.
            provider_system: System providing ``provided_service``.
            method: Method, if applicable, necessary to consume ``provided_service``.
            func: Function that performs the logic of the service.
            access_policy: Access policy used by service.
        """
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

    @property
    def protocol(self):
        return self._provided_service.interface.protocol

    def is_authorized(self, consumer_cert_str: str, auth_str: str):
        try:
            result = self._access_policy.is_authorized(consumer_cert_str, auth_str)  # type: ignore
        except errors.AuthorizationError:
            result = False

        return result


class OrchestrationRuleContainer(MutableMapping):
    """
    Orchestration Rule Container.

    This class is a thin wrapper around a dictionary, except for the :py:meth:`OrchestrationRuleContainer.store` method.
    """

    def __init__(self):
        self._rulecontainer: Dict[str, OrchestrationRule] = {}

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

    def __iter__(self) -> Iterator[str]:
        return iter(self._rulecontainer)

    def __len__(self) -> int:
        return len(self._rulecontainer)

    def store(self, item: OrchestrationRule):
        """
        Takes an OrchestrationRule and stores it with the key ``item.service_definition``

        Args:
            item: OrchestrationRule to be stored.
        """
        self._rulecontainer[item.service_definition] = item


class RegistrationRuleContainer:
    """
    Registration Rule Container
    """

    def __init__(self):
        self._rulecontainer: Dict[str, RegistrationRule] = {}

    def __iter__(self) -> Iterator[RegistrationRule]:
        return iter(self._rulecontainer.values())

    def __len__(self):
        return len(self._rulecontainer)

    def store(self, item: RegistrationRule):
        self._rulecontainer[item.service_definition] = item

    def retrieve(self, service_definition: str):
        return self._rulecontainer[service_definition]
