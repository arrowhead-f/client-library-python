from __future__ import annotations

from typing import Dict, Union, Optional, TypeVar, Generic, Type
from dataclasses import dataclass, field
import json

from pydantic import BaseModel

from arrowhead_client import constants

M = TypeVar('M', bound=BaseModel)

@dataclass
class Request(Generic[M]):
    body: bytes
    payload_type: str
    status: str | int = ''
    query: Dict = field(default_factory=dict)
    data_model: Type[M] | None = None

    # _request_object: Any

    @property
    def data(self) -> M:
        if self.data_model is None:
            raise RuntimeError("Request.data is only available if Request.data_model is not None")

        return self.data_model(**json.loads(self.body))

    def read_json(self, **kwargs):
        if self.payload_type != constants.Payload.JSON:
            raise RuntimeError(f'Body type must be \'{constants.Payload.JSON}\' '
                               f'to use read_json(), current type is {self.payload_type}')

        return json.loads(self.body)

    def read_string(self):
        return self.body.decode()
