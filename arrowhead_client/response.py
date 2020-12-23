from typing import Union, Dict
from dataclasses import dataclass
import json

from arrowhead_client.common import Constants


@dataclass
class Response:
    """
    Class for storing responses from systems
    """
    # TODO: This class is a bit clunky and causes bugs right now.
    payload: bytes
    payload_type: str
    status_code: Union[str, int]
    status_msg: str

    def read_json(self) -> Dict:
        if self.payload_type != Constants.PAYLOAD_JSON:
            raise RuntimeError(f'Payload type must be \'JSON\' to use read_json(), '
                               f'current type is {self.payload_type}')
        return json.loads(self.payload)

    def read_string(self) -> str:
        return self.payload.decode()

