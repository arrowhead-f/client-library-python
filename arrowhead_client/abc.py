from typing import Protocol, Any
from abc import ABC, abstractmethod

class BaseConsumer(Protocol):
    @abstractmethod
    def consume_service(self, service_definition: str, **kwargs) -> Any: # type: ignore
        raise NotImplementedError

    @abstractmethod
    def _extract_payload(self, service_response, interface):
        raise NotImplementedError

class BaseProvider(Protocol):
    pass

