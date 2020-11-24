from abc import abstractmethod
from typing import Callable
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
            provider: ArrowheadSystem,
            method: str,
            func: Callable,
            authorization_key, # TODO: Put this somewhere else
            *func_args,
            **func_kwargs, ) -> None:
        pass

    @abstractmethod
    def run_forever(self) -> None:
        pass
