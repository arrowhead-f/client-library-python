from abc import abstractmethod
from typing import Any, Callable
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


class BaseConsumer(Protocol):
    @abstractmethod
    def consume_service(
            self,
            service_uri: str,
            method: str,
            **kwargs) -> Any:  # type: ignore
        raise NotImplementedError

    @abstractmethod
    def extract_payload(
            self,
            service_response: Any,
            payload_type: str):
        raise NotImplementedError


class BaseProvider(Protocol):
    @abstractmethod
    def add_provided_service(
            self,
            service_definition: str,
            service_uri: str,
            method: str,
            func: Callable,
            *func_args,
            **func_kwargs, ) -> None:
        pass

    @abstractmethod
    def run_forever(self) -> None:
        pass
