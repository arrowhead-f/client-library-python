from abc import abstractmethod, ABC

from arrowhead_client.response import Response, ConnectionResponse
from arrowhead_client.rules import OrchestrationRule, RegistrationRule


class ProtocolMixin(ABC):
    def __init_subclass__(cls, protocol='', **kwargs):
        if protocol == '':
            raise ValueError('No protocol specified.')
        elif not isinstance(protocol, str):
            raise TypeError('Protocol must be of type str.')
        cls._protocol = protocol.upper()


class BaseConsumer(ProtocolMixin, ABC, protocol='<PROTOCOL>'):
    """Abstract base class for consumers"""
    def __init__(
            self,
            keyfile,
            certfile,
            cafile,
    ):
        self.keyfile = keyfile
        self.certfile = certfile
        self.cafile = cafile

    @abstractmethod
    def consume_service(
            self,
            rule: OrchestrationRule,
            **kwargs
    ) -> Response:
        """
        Consume service according to the consumation rule and return the response.

        Args:
           rule: Orchestration rule.
        Returns:
            A Response object.
        """

    async def connect(
            self,
            rule: OrchestrationRule,
            **kwargs,
    ) -> ConnectionResponse:
        """
        Connect to a service with a persistent connection, for example with WebSockets

        Args:
            rule: Orchestration rule.
        Returns:
            A connection object, currently implementation specific.
        """
        raise NotImplementedError

    async def async_startup(self):
        raise NotImplementedError

    def async_shutdown(self):
        raise NotImplementedError

class BaseProvider(ProtocolMixin, ABC, protocol='<PROTOCOL>'):
    """Abstract base class for providers"""
    def __init__(self, cafile: str):
        self.cafile = cafile

    @abstractmethod
    def add_provided_service(self, rule: RegistrationRule, ) -> None:
        """
        Adds the provided service to the provider according the provision rule.

        Args:
            rule: Provision rule.
        """

    @abstractmethod
    def run_forever(
            self,
            address: str,
            port: int,
            keyfile: str,
            certfile: str,
    ) -> None:
        """
        Starts the provider and runs until interrupted.

        Args:
            address: system ip address.
            port: system port.
            keyfile: client keyfile.
            certfile: client certfile.
            cafile: certificate authority file
        """
