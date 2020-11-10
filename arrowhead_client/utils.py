import re
from typing import Union, List


def uppercase_strings_in_list(requirement_list: Union[List[str], str]) -> List[str]:
    """
        Uppercases single string and puts it in a list,
        or uppercases strings in a list
    """
    if isinstance(requirement_list, str):
        return [requirement_list.upper()]
    elif isinstance(requirement_list, list):
        return [requirement.upper() for requirement in requirement_list]
    else:
        raise TypeError(
            "'requirement_list' is type {type(requirement_list)},"
            "should be type str or list(str)"
        )


def to_camel_case(variable_name: str) -> str:
    """ Turns snake_case variable name into camelCase """
    split_name = [split for split in variable_name.split('_') if split != '']
    initial_underscore = '_' if variable_name.startswith('_') else ''
    trailing_underscore = '_' if variable_name.endswith('_') else ''

    return initial_underscore + split_name[0] + \
        ''.join([split.capitalize() for split in split_name[1:]]) + trailing_underscore


def to_snake_case(variable_name: str) -> str:
    """ Turns camelCase variable name into snake_case """
    split_camel = re.findall(r'[A-Z][a-z0-9]*|[a-z0-9]+', variable_name)
    initial_underscore = '_' if variable_name.startswith('_') else ''
    trailing_underscore = '_' if variable_name.endswith('_') else ''

    return initial_underscore + \
        '_'.join([camel.lower() for camel in split_camel]) + trailing_underscore
