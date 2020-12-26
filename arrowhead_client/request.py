from typing import Any, Dict
from dataclasses import dataclass
import json

from common import Constants

@dataclass
class Request:
    body: bytes
    payload_type: str
    query: Dict
    # _request_object: Any

    @property
    def read_json(self):
        if self.payload_type == Constants.PAYLOAD_JSON:
            raise RuntimeError(f'Body type must be \'{Constants.PAYLOAD_JSON}\' '
                               f'to use read_json(), current type is {self.payload_type}')

        return json.loads(self.body)

    @property
    def read_string(self):
        return self.body.decode()