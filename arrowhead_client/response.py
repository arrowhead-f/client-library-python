from typing import Union, Dict
from dataclasses import dataclass


@dataclass
class Response:
    """
    Class for storing responses from systems
    """
    payload: Union[str, Dict, bytes]
    payload_type: str
    status_code: Union[str, int]
    status_msg: str
