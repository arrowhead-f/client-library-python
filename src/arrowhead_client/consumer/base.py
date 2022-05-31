from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Coroutine, Any

from arrowhead_client.abc import ProtocolMixin
from arrowhead_client.response import Response, ConnectionResponse
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.types import M


class BaseConsumer(ProtocolMixin, ABC, protocol='<PROTOCOL>'):
    """
    Abstract base class for consumers.

    Args:
        keyfile: Certificate keyfile.
        certfile: Certificate certfile.
        cafile: Certificate authority file.
    """

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
            data_model: type[M] | None = None,
            **kwargs,
    ) -> Response[M] | Coroutine[Any, Any, Response[M]]:
        """
        Consumes service according to the orchestrationrule.

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
        Connect to a service with a persistent connection, for example with WebSockets, according to the orchestration rule.

        Args:
            rule: Orchestration rule.
        Returns:
            A connection object, currently implementation specific.
        """
        raise NotImplementedError


class AsyncBaseConsumer(BaseConsumer, ABC, protocol='<PROTOCOL>'):
    @abstractmethod
    async def consume_service(
            self,
            rule: OrchestrationRule,
            data_model: type[M] | None = None,
            **kwargs,
    ) -> Response[M]:
        ...

    async def async_startup(self):
        raise NotImplementedError

    def async_shutdown(self):
        raise NotImplementedError
