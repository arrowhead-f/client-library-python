from typing import Union, Dict
from dataclasses import dataclass


@dataclass
class Response:
    """
    Class for storing responses from systems
    """
    # TODO: This class is a bit clunky and causes bugs right now.
    payload: Union[str, Dict, bytes]
    payload_type: str
    status_code: Union[str, int]
    status_msg: str
