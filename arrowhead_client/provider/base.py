from abc import ABC, abstractmethod

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