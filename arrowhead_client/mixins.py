from abc import ABC
from typing import Dict, Union, Set

from arrowhead_client import utils


class DTOMixin(ABC):
    """ Mixin to create data-transfer objects from class """

    _dto_excludes: Set[str] = set()
    _dto_property_include: Set[str] = set()

    @property
    def dto(self, excludes: Set = None) -> Dict[str, Dict[str, Union[str, bool]]]:
        excludes = excludes or set()
        from_vars = {utils.to_camel_case(variable_name): variable for
                     variable_name, variable in vars(self).items()
                     if variable_name not in self._dto_excludes
                     and variable_name not in excludes}
        from_properties = {utils.to_camel_case(property_name): getattr(self, property_name) for
                           property_name in self._dto_property_include}
        return {**from_vars, **from_properties}


