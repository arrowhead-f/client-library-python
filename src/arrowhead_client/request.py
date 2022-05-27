from typing import Dict, Union, Optional, TypeVar, Generic
from dataclasses import dataclass, field
import json

from pydantic import BaseModel

from arrowhead_client import constants

M = TypeVar('M', bound=BaseModel)

@dataclass
class Request(Generic[M]):
    body: bytes
    payload_type: str
    status: Union[str, int] = ''
    query: Dict = field(default_factory=dict)
    data_model: Optional[M] = None

    # _request_object: Any

    def read_json(self):
        if self.payload_type != constants.Payload.JSON:
            raise RuntimeError(f'Body type must be \'{constants.Payload.JSON}\' '
                               f'to use read_json(), current type is {self.payload_type}')

        return json.loads(self.body)

    def read_string(self):
        return self.body.decode()
