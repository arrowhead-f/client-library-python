from __future__ import annotations

from functools import partial
from typing import Any, Callable, Type, Sequence, ClassVar, get_type_hints, TypeVar, Coroutine, Mapping

from arrowhead_client.response import Response

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from pydantic import BaseModel

from arrowhead_client.request import Request
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.provider.base import BaseProvider
from arrowhead_client.consumer.base import BaseConsumer
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.client.core_services import get_core_rules
from arrowhead_client.logs import get_logger
from arrowhead_client.client.core_system_defaults import config as ar_config
from arrowhead_client.security.access_policy import get_access_policy
from arrowhead_client.rules import (
    OrchestrationRuleContainer,
    RegistrationRuleContainer,
    RegistrationRule,
    EventSubscriptionRule,
)
from arrowhead_client import constants
from arrowhead_client.types import Metadata, M


class ServiceDescriptorBase:
    def __init__(self, func: Callable[[Any, Request], Any]):
        ...


def provided_service(
    service_definition: str,
    service_uri: str,
    protocol: str,
    method: str,
    payload_format: str,
    access_policy: str,
) -> Type[ServiceDescriptorBase]:
    """
    Decorator to create services bound to subclasses of ArrowheadClient.
    Should be used when the client needs to manage states, for example a counter of how many times a service has been accessed, see example below.

    Args:
        service_definition: Service definition string registered in the service registry.
        service_uri: Service identifier string, for example the path of a HTTP url.
        protocol: Protocol used by this service (e.g. HTTP and WS).
        method: Command used by the protocol (e.g. HTTP GET or POST). If the protocol does use a command (e.g. WS), this should be '*'.
        payload_format: The payload_format of the payload (e.g. JSON, XML, or TEXT).
        access_policy: :code:`'UNRESTRICTED'` if system is in insecure mode, :code:`'CERTIFICATE'` or :code:`'TOKEN'` if system is in secure_string mode.

    Returns:
        A ServiceDescriptor object

    Example::

        class TestClient(AsyncClient):
            def __init__(self):
                self.counter = 0

            '''
            This service will be registered as 'list_reverser'
            with uri 'https://127.0.0.1:5678/reverse/'. The
            address and port are system specific.
            '''
            @provided_service(
                    service_definition='list_reverser',
                    service_uri='reverse',
                    protocol='http',
                    method='POST',
                    payload_format='TEXT',
                    access_policy='NOT_SECURE',
            )
            async def reverse(self, input: List[str]):
                self.counter += 1
                return list(reversed(input))
    """

    class ServiceDescriptor(ServiceDescriptorBase):
        data_model: type[BaseModel] | None
        def __init__(self, func: Callable[[Any, Request], Any]):
            super().__init__(func)
            self.service_instance = Service.make(
                service_definition,
                service_uri,
                protocol,
                access_policy,
                payload_format,
            )
            self.method = method
            self.service_definition = service_definition
            self.func = func

            try:
                self.data_model = get_args(
                    get_type_hints(func)["req"]
                )[0]
            except IndexError:
                self.data_model = None

        def __set_name__(self, owner: type[ArrowheadClient], name: str):
            if "__arrowhead_services__" not in dir(owner):
                raise AttributeError(
                    "provided_service can only decorate ArrowheadClient methods."
                )

            owner.__arrowhead_services__ += (name,)

        def __get__(self, instance: ArrowheadClient, owner: type[ArrowheadClient]):
            if instance is None:
                return self

            return RegistrationRule(
                provided_service=self.service_instance,
                provider_system=instance.system,
                method=self.method,
                func=partial(self.func, instance),
                data_model=self.data_model,
            )

    return ServiceDescriptor


def subscribed_event(
    event_type: str,
    metadata: Metadata | None = None,
):
    class EventDescriptor:
        def __init__(self, callback: Callable):
            self.event_type = event_type
            self.metadata = metadata
            self.callback = callback

        def __set_name__(self, owner: type[ArrowheadClient], name: str):
            if "__arrowhead_subscribed_events__" not in dir(owner):
                raise AttributeError(
                    "subscribed_event can only decorate ArrowheadClient methods."
                )

            owner.__arrowhead_subscribed_events__ += (name,)

        def __get__(self, instance: ArrowheadClient, owner: Type[ArrowheadClient]):
            if instance is None:
                return self

            return EventSubscriptionRule(
                event_type=self.event_type,
                subscriber_system=instance.system,
                callback=self.callback,
                metadata=self.metadata,
            )

    return EventDescriptor


class ArrowheadClient(ABC):
    """
    Base class for Arrowhead Clients.

    This class serves as a bridge that connects systems, consumers, and providers to the user.

    ArrowheadClient should not be used or subclassed directly,
    use :py:class:`ArrowheadClientSync` or :py:class:`ArrowheadClientAsync` for those needs instead.

    To instantiate an ArrowheadClient, use the :py:meth:`~ArrowheadClient.create` classmethod instead of :code:`ArrowheadClient()`.

    The arguments given to ``__init__`` which are stored as-is:

    Args:
        system: System managed by the client.
        consumer: Consumer used to consume services.
        provider: Provider used to provide services.
        logger: Logger object.
        keyfile: PEM keyfile.
        certfile: PEM certfile.
        config: Config dictionary, format not yet decided.

    In addition to the arguments mentioned above, ``__init__`` also generates the following attributes:

    Attributes:
        secure: ``True`` if keyfile and certfile are both given, which means the client will run in secure_string mode.
        auth_authentication_info: Authorization system certificate string. It is attained when a connection to a secure local cloud is established.
        orchestration_rules: Mapping containing the rules with the information necessary to perform service consumption.
        registration_rules: Mapping containing the rules with the information necessary to perform service registration.
    """

    def __init__(
        self,
        system: ArrowheadSystem,
        consumers: Sequence[BaseConsumer],
        provider: BaseProvider,
        logger: Any,
        config: Mapping = None,
        keyfile: str = "",
        certfile: str = "",
        **kwargs,
    ):
        self.system = system
        self.consumers: Mapping[str, BaseConsumer] = {
            protocol: consumer
            for consumer in consumers
            for protocol in consumer._protocol
        }
        self.provider = provider
        self.keyfile = keyfile
        self.certfile = certfile
        self.secure = all(self.cert)
        self._logger = logger
        self.config = config or ar_config
        self.auth_authentication_info = None
        self.orchestration_rules = OrchestrationRuleContainer()
        self.registration_rules = RegistrationRuleContainer()
        self.event_subscription_rules: dict[str, EventSubscriptionRule] = {}
        # TODO: Should add_provided_service be exactly the same as the provider's,
        # or should this class do something on top of it?
        # It's currently not even being used so it could likely be removed.
        # Maybe it should be it's own method?
        self.add_provided_service = self.provider.add_provided_service

    __arrowhead_services__: ClassVar[tuple[str, ...]] = ()
    __arrowhead_subscribed_events__: ClassVar[tuple[str, ...]] = ()
    __arrowhead_consumers__: ClassVar[Sequence[type[BaseConsumer]]]
    __arrowhead_provider__: ClassVar[type[BaseProvider]]

    # TODO: Remove this property, it is requests specific
    @property
    def cert(self) -> tuple[str, str]:
        """Tuple of the keyfile and certfile"""
        return self.certfile, self.keyfile

    def setup(self):
        # Setup methods
        self._core_service_setup()

        # Setup services defined by method decorators
        for class_service_rule in self.__arrowhead_services__:
            self.registration_rules.store(getattr(self, class_service_rule))

        # Setup event subscriptions defined by method decorators
        for class_event_subscription in self.__arrowhead_subscribed_events__:
            self.event_subscription_rules[class_event_subscription] = getattr(
                self, class_event_subscription
            )

    def provided_service(
        self,
        service_definition: str,
        service_uri: str,
        protocol: str,
        method: str,
        payload_format: str,
        access_policy: str,
        data_model: type[BaseModel] | None = None,
    ) -> Callable[[Callable[[Request], Any]], Callable[[Request], Any]]:
        """
        Decorator to add a provided provided_service to the provider.
        Useful during testing, because unlike the free :code:`provided_service` decorator this one does not require subclassing :code:`ArrowheadClient`.

        Args:
            service_definition: Service definition to be stored in the provided_service registry
            service_uri: The path to the provided_service
            protocol:
            method: HTTP method required to access the provided_service

        Example::

            provider = SomeClient.create(...)

            @provider.provided_service(
                    service_definition='list_reverser',
                    service_uri='reverse',
                    protocol='http',
                    method='POST',
                    payload_format='TEXT',
                    access_policy='NOT_SECURE',
            )
            async def reverse(input: List[str]):
                return list(reversed(input))
        """

        provided_service = Service(
            service_definition,
            service_uri,
            ServiceInterface.with_access_policy(
                protocol,
                access_policy,
                payload_format,
            ),
            access_policy,
        )

        def wrapped_func(func: Callable[[Request], Any]):
            try:
                data_model = get_args(
                        get_type_hints(func)["req"]
                )[0]
            except IndexError:
                self.data_model = None

            self.registration_rules.store(
                RegistrationRule(
                    provided_service,
                    self.system,
                    method,
                    func,
                    data_model=data_model,
                )
            )
            return func

        return wrapped_func

    def subscribed_event(
        self,
        event_type: str,
        metadata: Metadata | None = None,
    ):
        """
        Decorator for subscribing to events.

        Args:
            event_type: Name of event type that will be published.
            metadata: Dictionary of metadata.
        Returns:

        """

        def decorator(func: Callable):
            self.event_subscription_rules[event_type] = EventSubscriptionRule(
                event_type=event_type,
                subscriber_system=self.system,
                metadata=metadata,
                callback=func,
            )

            return func

        return decorator

    @abstractmethod
    def add_orchestration_rule(
        self,
        service_definition: str,
        method: str,
        protocol: str = "",
        access_policy: str = "",
        payload_format: str = "",
        # TODO: Should **kwargs be preferred_providers?
        orchestration_flags: constants.OrchestrationFlags = constants.OrchestrationFlags.OVERRIDE_STORE,
        data_model: type[M] | None = None,
        **kwargs,
    ) -> None:
        """
        Looks up orchestration rules in the Orchestration system.

        If one of :code:`method`, :code:`access_policy`, and :code:`payload` is given, the other two must be given as well.

        Args:
            service_definition: Service definition that is looked up from the orchestrator.
            method: Optional. The HTTP method given in uppercase that is used to consume the provided_service.
            access_policy: Optional. Service access policy.
            payload_format: Optional. Service payload format.
            orchestration_flags: Optional. Sets orchestration mode.
            data_model: Optional. Type derived from Pydantic.BaseModel.

        Example::

            example_client = SyncClient(...)

            ...

            # Find orchestration rules for service :code:`echo` with
            example_client.add_orchestration_rule('echo', 'GET')

            ...

        """

    @abstractmethod
    def consume_service(self, service_definition: str, data_model: type[M] | None = None, **kwargs) -> Response[M] | Coroutine[Any, Any, Response[M]]:
        """
        Consumes the given provided_service definition.

        Will raise an error if no orchestration rules exist for the given service definition.

        Args:
            service_definition: The provided_service definition of a consumable provided_service
            data_model: Pydantic model used to deserialize the received message
            **kwargs: Collection of keyword arguments passed to the consumer.

        Example::

            example_client = SyncClient(...)

            ...

            response = example_client.consume('echo')
            body = handle_echo_response(response)

            ...
        """

    @abstractmethod
    def publish_event(self, event_type: str, payload: str | bytes | dict):
        pass

    @abstractmethod
    def run_forever(self):
        """
        Start the server, publish all provided_service, and run until interrupted.

        Note, this method only needs to be run when the client is providing a service or if the client intends
        to use the Eventhandler core system.
        """
        pass

    _T = TypeVar('_T', bound="ArrowheadClient")

    @classmethod
    def create(
        cls: type[_T],
        system_name: str,
        address: str,
        port: int,
        config: dict = None,
        keyfile: str = "",
        certfile: str = "",
        cafile: str = "",
        log_mode: str = "debug",
        **kwargs,
    ) -> _T:
        """
        Factory method for client instances.
        This is the preferred way of creating class instances because it takes care of instantiating producers,
        consumers, and logging properly.

        If you wish to use different producers or consumers, create a new class inheriting from either
        :code:`client.ArrowheadClientAsync` or :code:`client.ArrowheadClientSync` and specify the
        :code:`__arrowhead_provider__` and :code:`__arrowhead_consumers__` fields.

        Args:
            system_name: Name for the system the client will register as in the service and system registries.
            address: System address.
            port: System port.
            config: Config object, format not yet specified. Optional.
            keyfile: Path to a PEM keyfile. If you use pkcs#12 keystores, you need to convert them to PEM format first.
            certfile: Path to a PEM certfile. If you use pkcs#12 keystores, you need to convert them to PEM format first.
            cafile: Path to a PEM certificate authority file. If you use pkcs#12 keystores, you need to convert them to PEM format first.
        Returns:
            A new ArrowheadClient instance.

        Example::

            from arrowhead_client.implementations import AsyncClient

            example_client = AsyncClient.create(
                    system_name='example_client',
                    address='127.0.0.1',
                    port=5678,
                    config=example_config,
                    keyfile='certificates/example.key',
                    certfile='certificates/example.pem',
                    cafile='certificates/example_cloud.ca',
            )
        """
        logger = get_logger(system_name, log_mode)
        system = ArrowheadSystem.with_certfile(
            system_name,
            address,
            port,
            certfile,
        )
        new_instance = cls(
            system=system,
            consumers=tuple(
                consumer(keyfile, certfile, cafile)
                for consumer in cls.__arrowhead_consumers__
            ),
            provider=cls.__arrowhead_provider__(cafile),
            logger=logger,
            config=config,
            keyfile=keyfile,
            certfile=certfile,
            **kwargs,
        )

        return new_instance

    @classmethod
    def from_yaml(
        cls,
        config_path: str,
        **kwargs,
    ):
        """
        Factory method to create

        Args:
            config_path: Path to config_file
            **kwargs: Keyword arguments going into ArrowheadClient.create()
        Returns:
            ArrowheadClient instance with parameters from config.
        """
        with open(config_path, "r") as yamlfile:
            config = yaml.safe_load(yamlfile)["client"]

        return cls.create(**{**config, **kwargs})

    @classmethod
    def from_config(cls, config_path: str, **kwargs):
        config_type = Path(config_path).suffix

        if config_type == ".yaml":
            return cls.from_yaml(config_path, **kwargs)
        else:
            raise ValueError(f"Configuration file format {config_type} unsupported")

    @abstractmethod
    def _register_service(self, service):
        """
        Registers the given provided_service with provided_service registry

        Args:
            service: Service to register with the Service registry.
        """
        pass

    @abstractmethod
    def _register_all_services(self):
        """
        Registers all provided services of the system with the system registry.
        """
        pass

    @abstractmethod
    def _unregister_service(self, service):
        """
        Unregisters the given provided_service with provided_service registry

        Args:
            service: Service to unregister with the Service registry.
        """
        pass

    @abstractmethod
    def _unregister_all_services(self):
        """
        Unregisters all provided services of the system with the system registry.
        """
        pass

    @abstractmethod
    def _subscribe_event(self, event_type):
        """
        Subscribes to event
        """

    @abstractmethod
    def _subscribe_all_events(self):
        """
        Subscribes to all events.
        """

    @abstractmethod
    def _unsubscribe_event(self, event_type):
        """
        Unsubscribe to event.
        """

    @abstractmethod
    def _unsubscribe_all_events(self):
        """
        Unsubscribe to all events.
        """

    def _initialize_provided_services(self) -> None:
        for rule in self.registration_rules:
            rule.access_policy = get_access_policy(
                policy_name=rule.provided_service.access_policy,
                provided_service=rule.provided_service,
                privatekey=self.keyfile,
                authorization_key=self.auth_authentication_info,
            )
            self.provider.add_provided_service(rule)

    def _initialize_event_subscription(self) -> None:
        for event_type, rule in self.event_subscription_rules.items():
            fake_service = Service(
                service_definition=f"{event_type}-{rule.uuid}",
                service_uri=rule.notify_uri,
                interface=ServiceInterface.from_str("HTTP-SECURE-JSON"),
            )
            fake_access_policy = get_access_policy(
                policy_name=constants.AccessPolicy.CERTIFICATE,
                provided_service=fake_service,
                privatekey=self.keyfile,
                authorization_key=self.auth_authentication_info,
            )
            fake_registration_rule = RegistrationRule(
                provided_service=fake_service,
                provider_system=rule.subscriber_system,
                method="POST",
                access_policy=fake_access_policy,
                func=rule.callback,
            )
            self.provider.add_provided_service(fake_registration_rule)

    def _core_service_setup(self) -> None:
        """
        Method that sets up the test_core services.

        Runs when the client is created and should not be run manually.
        """

        core_rules = get_core_rules(self.config, self.secure)

        for rule in core_rules:
            self.orchestration_rules.store(rule)

    def _update_certificates(
        self, new_certfile: Path, new_keyfile: Path, new_cafile: Path | None = None
    ):
        if (
            not new_certfile.is_file()
            or not new_keyfile.is_file()
            or (new_cafile is not None and not new_cafile.is_file())
        ):
            raise ValueError("New certificate files need to exist")
        # TODO: Check that files contain valid X509 information?

        self.certfile = new_certfile.as_uri()
        self.keyfile = new_keyfile.as_uri()

        if new_cafile is not None:
            self.provider.cafile = new_cafile.as_uri()

        for protocol, consumer in self.consumers.items():
            consumer.certfile = new_certfile
            consumer.keyfile = new_keyfile
            if new_cafile is not None:
                consumer.cafile = new_cafile
