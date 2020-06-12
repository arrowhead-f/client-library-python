from typing import Protocol, Any, Callable
from abc import ABC, abstractmethod

class BaseConsumer(Protocol):
    @abstractmethod
    def consume_service(self, service_uri: str, method: str, **kwargs) -> Any: # type: ignore
        raise NotImplementedError

    @abstractmethod
    def _extract_payload(self, service_response, interface):
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
            **func_kwargs,
            ) -> None:
        pass

    @abstractmethod
    def run_forever(self):
        pass

