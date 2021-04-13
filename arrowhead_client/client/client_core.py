from __future__ import annotations

from functools import partial
from typing import Any, Dict, Tuple, Callable, Type, List, Optional
from abc import ABC, abstractmethod

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
)
from arrowhead_client import constants


def provided_service(
        service_definition: str,
        service_uri: str,
        protocol: str,
        method: str,
        payload_format: str,
        access_policy: str,
):
    """
    Decorator to create services bound to subclasses of ArrowheadClient.
    Should be used when the client needs to manage states, for example a counter of how many times a service has been accessed, see example below.

    Args:
        service_definition: Service definition string registered in the service registry.
        service_uri: Service identifier string, for example the path of a HTTP url.
        protocol: Protocol used by this service (e.g. HTTP and WS).
        method: Command used by the protocol (e.g. HTTP GET or POST). If the protocol does use a command (e.g. WS), this should be '*'.
        payload_format: The payload_format of the payload (e.g. JSON, XML, or TEXT).
        access_policy: :code:`'UNRESTRICTED'` if system is in insecure mode, :code:`'CERTIFICATE'` or :code:`'TOKEN'` if system is in secure mode.

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

    class ServiceDescriptor:
        def __init__(self, func):
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

        def __set_name__(self, owner: Type[ArrowheadClient], name: str):
            if '__arrowhead_services__' not in dir(owner):
                raise AttributeError('provided_service can decorate ArrowheadClient methods.')

            owner.__arrowhead_services__.append(name)

        def __get__(self, instance: ArrowheadClient, owner: Type[ArrowheadClient]):
            if instance is None:
                return self

            return RegistrationRule(
                    provided_service=self.service_instance,
                    provider_system=instance.system,
                    method=self.method,
                    func=partial(self.func, instance),
            )

    return ServiceDescriptor


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
        secure: ``True`` if keyfile and certfile are both given, which means the client will run in secure mode.
        auth_authentication_info: Authorization system certificate string. It is attained when a connection to a secure local cloud is established.
        orchestration_rules: Mapping containing the rules with the information necessary to perform service consumption.
        registration_rules: Mapping containing the rules with the information necessary to perform service registration.
    """

    def __init__(
            self,
            system: ArrowheadSystem,
            consumer: BaseConsumer,
            provider: BaseProvider,
            logger: Any,
            config: Dict = None,
            keyfile: str = '',
            certfile: str = '',
            **kwargs,
    ):
        self.system = system
        self.consumer = consumer
        self.provider = provider
        self.keyfile = keyfile
        self.certfile = certfile
        self.secure = all(self.cert)
        self._logger = logger
        self.config = config or ar_config
        self.auth_authentication_info = None
        self.orchestration_rules = OrchestrationRuleContainer()
        self.registration_rules = RegistrationRuleContainer()
        # TODO: Should add_provided_service be exactly the same as the provider's,
        # or should this class do something on top of it?
        # It's currently not even being used so it could likely be removed.
        # Maybe it should be it's own method?
        self.add_provided_service = self.provider.add_provided_service

    __arrowhead_services__: List[str] = []
    __arrowhead_consumer__: Type[BaseConsumer]
    __arrowhead_provider__: Type[BaseProvider]

    @property
    def cert(self) -> Tuple[str, str]:
        """ Tuple of the keyfile and certfile """
        return self.certfile, self.keyfile

    def setup(self):
        # Setup methods
        self._core_service_setup()

        for class_service_rule in self.__arrowhead_services__:
            self.registration_rules.store(getattr(self, class_service_rule))

    def provided_service(
            self,
            service_definition: str,
            service_uri: str,
            protocol: str,
            method: str,
            payload_format: str,
            access_policy: str,
    ) -> Callable:
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

        def wrapped_func(func):
            self.registration_rules.store(
                    RegistrationRule(
                            provided_service,
                            self.system,
                            method,
                            func,
                    )
            )
            return func

        return wrapped_func

    @abstractmethod
    def add_orchestration_rule(
            self,
            service_definition: str,
            method: str,
            protocol: str = '',
            access_policy: str = '',
            payload_format: str = '',
            # TODO: Should **kwargs be preferred_providers?
            orchestration_flags: constants.OrchestrationFlags = constants.OrchestrationFlags.OVERRIDE_STORE,
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

        Example::

            example_client = SyncClient(...)

            ...

            # Find orchestration rules for service :code:`echo` with
            example_client.add_orchestration_rule('echo', 'GET')

            ...

        """

    @abstractmethod
    def consume_service(self, service_definition, **kwargs):
        """
        Consumes the given provided_service definition.

        Will raise an error if no orchestration rules exist for the given service definition.

        Args:
            service_definition: The provided_service definition of a consumable provided_service
            **kwargs: Collection of keyword arguments passed to the consumer.

        Example::

            example_client = SyncClient(...)

            ...

            response = example_client.consume('echo')
            data = handle_echo_response(response)

            ...
        """
        pass

    @abstractmethod
    def run_forever(self):
        """
        Start the server, publish all provided_service, and run until interrupted.

        Note, this method only needs to be run when the client is providing a service or if the client intends
        to use the Eventhandler core system.
        """
        pass

    @classmethod
    def create(
            cls,
            system_name: str,
            address: str,
            port: int,
            config: Dict = None,
            keyfile: str = '',
            certfile: str = '',
            cafile: str = '',
            log_mode: str = 'debug',
            **kwargs,
    ) -> ArrowheadClient:
        """
        Factory method for client instances.
        This is the preferred way of creating class instances because it takes care of instantiating producers,
        consumers, and logging properly.

        If you wish to use different producers or consumers, create a new class inheriting from either
        :code:`client.ArrowheadClientAsync` or :code:`client.ArrowheadClientSync` and specify the
        :code:`__arrowhead_provider__` and :code:`__arrowhead_consumer__` fields.

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
                system,
                cls.__arrowhead_consumer__(keyfile, certfile, cafile),
                cls.__arrowhead_provider__(cafile),
                logger,
                config=config,
                keyfile=keyfile,
                certfile=certfile,
                **kwargs
        )

        return new_instance

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

    def _initialize_provided_services(self) -> None:
        for rule in self.registration_rules:
            rule.access_policy = get_access_policy(
                    policy_name=rule.provided_service.access_policy,
                    provided_service=rule.provided_service,
                    privatekey=self.keyfile,
                    authorization_key=self.auth_authentication_info
            )
            self.provider.add_provided_service(rule)

    def _core_service_setup(self) -> None:
        """
        Method that sets up the test_core services.

        Runs when the client is created and should not be run manually.
        """

        core_rules = get_core_rules(self.config, self.secure)

        for rule in core_rules:
            self.orchestration_rules.store(rule)
