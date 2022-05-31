from pydantic import BaseModel
from typing import Mapping, Union, TypeVar

Metadata = Mapping[str, str]
Version = Union[int, str]
M = TypeVar('M', bound=BaseModel)