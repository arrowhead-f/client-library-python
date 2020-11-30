from abc import abstractmethod, ABC
from typing import Callable, Tuple

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore
from arrowhead_client.response import Response
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem


class BaseConsumer(Protocol):
    @abstractmethod
    def consume_service(
            self,
            service: Service,
            system: ArrowheadSystem,
            method: str,
            token: str,
            **kwargs) -> Response:
        raise NotImplementedError

    @abstractmethod
    def extract_payload(
            self,
            service_response: Response,
            payload_type: str):
        raise NotImplementedError


class BaseProvider(Protocol):
    @abstractmethod
    def add_provided_service(
            self,
            service: Service,
            #provider: ArrowheadSystem,
            method: str,
            func: Callable,
            authorization_key, # TODO: Put this somewhere else
            *func_args,
            **func_kwargs, ) -> None:
        raise NotImplementedError

    @abstractmethod
    def run_forever(self) -> None:
        raise NotImplementedError


class AccessPolicy(ABC):
    """
    Abstract class that describes the interface for access policies.
    """
    @abstractmethod
    def is_authorized(self,
                      consumer_cn: str,
                      provider: ArrowheadSystem,
                      provided_service: Service,
                      token: str,
                      **kwargs, ) -> Tuple[bool, str]:
        """
        Check if consumer is authorized to consume the provided service.

        Args:
            consumer_cn: Common name of consumer extracted from the consumer certificate.
            provider: System providing the service.
            provided_service: The provided service.
            token: Token used with the token access policy.
            kwargs: Possible extra arguments.
        Returns:
            A tuple with a bool value and message string.
            If authorization is successful, the value will be :code:`(True, '')`,
            but if the authorization is unsuccessful value will be :code:`(False, <message>)`,
            where the message will contain information about what went wrong in the
            authorization process.

        """
        raise NotImplementedError