from typing import Union, Dict, Optional
from dataclasses import dataclass
import json


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

    def read_json(self) -> Optional[Dict]:
        try:
            return json.loads(self.payload)
        except json.JSONDecodeError as e:
            return None

    def read_string(self) -> str:
        return self.payload.decode()

