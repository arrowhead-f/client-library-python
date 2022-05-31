from __future__ import annotations

from dataclasses import dataclass, field
import json
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union

from pydantic import BaseModel

from arrowhead_client import constants


M = TypeVar('M', bound=BaseModel)

@dataclass
class Response(Generic[M]):
    """
    Class for storing responses from systems
    """
    body: bytes
    payload_type: str
    status_code: str | int
    data_model: type[M] | None = None

    @property
    def data(self) -> M:
        if self.data_model is None:
            raise RuntimeError("Response.data can only be used if Response.data_model is not None.")
        return self.data_model(**json.loads(self.body))

    def read_json(self) -> dict:
        if self.payload_type != constants.Payload.JSON:
            raise RuntimeError(f'Payload type must be \'{constants.Payload.JSON}\' to use read_json(), '
                               f'current type is {self.payload_type}')

        try:
            return json.loads(self.body)
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Payload of type \'{constants.Payload.JSON}\' '
                               f'is unable to be decoded. Current payload is:\n'
                               f' {self.body.decode()}') from e

    def read_string(self) -> str:
        return self.body.decode()


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
