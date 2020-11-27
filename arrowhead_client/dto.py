from abc import ABC
from typing import Dict, Set, Iterable

from arrowhead_client import utils

class DTOMixin(ABC):
    """ Mixin to create data-transfer objects from class """

    # Members to be excluded from the dto
    _dto_excludes: Set[str] = set()
    # Properties to be included in the dto
    _dto_property_include: Set[str] = set()

    def dto(self, exclude: Iterable[str] = None) -> Dict:
        exclude = exclude or set()
        # Check that all names in exclude are members of self
        if not exclude <= set(dir(self)):
            raise ValueError(f'Name in {exclude} is not a member of {self}')
        # Get variables and values
        from_vars = {utils.to_camel_case(variable): value for
                     variable, value in vars(self).items()
                     if variable not in self._dto_excludes
                     and variable not in exclude}
        # Get properties and property values
        from_properties = {utils.to_camel_case(property): getattr(self, property) for
                           property in self._dto_property_include
                           if property not in exclude}

        return {**from_vars, **from_properties}
