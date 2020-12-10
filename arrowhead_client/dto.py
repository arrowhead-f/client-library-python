import re
from abc import ABC
from typing import Dict, Set, Iterable


class DTOMixin(ABC):
    """ Mixin to create data-transfer objects from class """

    # TODO: Make sure these two cannot be set to invalid values
    # Members to be excluded from the dto
    _dto_excludes: Set[str] = set()
    # Properties to be included in the dto
    _dto_property: Set[str] = set()

    def dto(self, exclude: Iterable[str] = None) -> Dict:
        exclude = set(exclude) if exclude else set()
        # Check that all names in exclude are members of self
        if not exclude <= set(dir(self)):
            raise ValueError(f'Name in {exclude} is not a member of {self}')
        # Get variables and values
        from_vars = {to_camel_case(variable): value for
                     variable, value in vars(self).items()
                     if variable not in self._dto_excludes
                     and variable not in exclude}
        # Get properties and property values
        from_properties = {to_camel_case(property): getattr(self, property) for
                           property in self._dto_property
                           if property not in exclude}

        return {**from_vars, **from_properties}


def to_camel_case(variable_name: str) -> str:
    """ Turns snake_case string into camelCase """
    first_split, *split_name = [split for split in variable_name.split('_') if split != '']
    initial_underscore = '_' if variable_name.startswith('_') else ''
    trailing_underscore = '_' if variable_name.endswith('_') else ''

    return initial_underscore + first_split + \
        ''.join([split.capitalize() for split in split_name]) + trailing_underscore


def to_snake_case(variable_name: str) -> str:
    """ Turns camelCase string into snake_case """
    split_camel = re.findall(r'[A-Z][a-z0-9]*|[a-z0-9]+', variable_name)
    initial_underscore = '_' if variable_name.startswith('_') else ''
    trailing_underscore = '_' if variable_name.endswith('_') else ''

    return initial_underscore + \
        '_'.join([camel.lower() for camel in split_camel]) + trailing_underscore
