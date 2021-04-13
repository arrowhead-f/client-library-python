from abc import ABC, abstractmethod
from typing import Callable

from arrowhead_client.abc import ProtocolMixin
from arrowhead_client.rules import RegistrationRule


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

    def add_startup_routine(self, func: Callable):
        """
        Schedules ``func`` to be called during startup.

        Args:
            func: Function executed during startup, must not take any arguments.
        """
        raise NotImplementedError

    def add_shutdown_routine(self, func: Callable):
        """
        Schedules ``func`` to be called during shutdown.

        Args:
            func: Function executed during shutdown, must not take any arguments.
        """
        raise NotImplementedError
