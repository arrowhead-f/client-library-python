from typing import Union, Dict
from dataclasses import dataclass
import json
from abc import ABC, abstractmethod

from arrowhead_client import constants


@dataclass
class Response:
    """
    Class for storing responses from systems
    """
    payload: bytes
    payload_type: str
    status_code: Union[str, int]

    def read_json(self) -> Dict:
        if self.payload_type != constants.Payload.JSON:
            raise RuntimeError(f'Payload type must be \'{constants.Payload.JSON}\' to use read_json(), '
                               f'current type is {self.payload_type}')

        try:
            return json.loads(self.payload)
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Payload of type \'{constants.Payload.JSON}\' '
                               f'is unable to be decoded. Current payload is:\n'
                               f' {self.payload.decode()}') from e

    def read_string(self) -> str:
        return self.payload.decode()


class ConnectionResponse(ABC):
    """
    Adapter for websockets
    """

    def __init__(
            self,
            connector,
    ):
        self._connector = connector

    @abstractmethod
    async def send(self, data):
        pass

    @abstractmethod
    async def receive(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
