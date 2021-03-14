from typing import Dict, Union
from dataclasses import dataclass, field
import json

from arrowhead_client import constants


@dataclass
class Request:
    body: bytes
    payload_type: str
    status: Union[str, int] = ''
    query: Dict = field(default_factory=dict)

    # _request_object: Any

    def read_json(self):
        if self.payload_type != constants.Payload.JSON:
            raise RuntimeError(f'Body type must be \'{constants.Payload.JSON}\' '
                               f'to use read_json(), current type is {self.payload_type}')

        return json.loads(self.body)

    def read_string(self):
        return self.body.decode()
