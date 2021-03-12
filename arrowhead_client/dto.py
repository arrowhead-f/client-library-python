"""
DTO Module
==========

Contains the :py:class:`~arrowhead_client.dto.DTOMixin` class.
"""
import re
from abc import ABC
from datetime import datetime, timedelta

from pydantic import BaseModel
from pydantic.json import timedelta_isoformat, isoformat

from arrowhead_client.service import ServiceInterface


def to_camel_case(variable_name: str) -> str:
    """
    Turns snake_case string into camelCase.

    Args:
        variable_name: variable name in ``snake_case_form``.
    Returns:
        variable_name in ``camelCaseForm``.
    """
    first_split, *split_name = [split for split in variable_name.split('_') if split != '']
    initial_underscore = '_' if variable_name.startswith('_') else ''
    trailing_underscore = '_' if variable_name.endswith('_') else ''

    return initial_underscore + first_split + \
           ''.join([split.capitalize() for split in split_name]) + trailing_underscore


def to_snake_case(variable_name: str) -> str:
    """
    Turns camelCase string into snake_case.

    Args:
        variable_name: Variable name in ``camelCaseForm``.
    Returns:
        variable_name in ``snake_case_form``.
    """
    split_camel = re.findall(r'[A-Z][a-z0-9]*|[a-z0-9]+', variable_name)
    initial_underscore = '_' if variable_name.startswith('_') else ''
    trailing_underscore = '_' if variable_name.endswith('_') else ''

    return initial_underscore + \
           '_'.join([camel.lower() for camel in split_camel]) + trailing_underscore


class DTOMixin(ABC, BaseModel):
    """
    Mixin to create data-transfer objects from class.

    This class is a customized version of :py:class:`pydantic.BaseModel`, which gives it some quirks:

     * When subclassing ``DTOMixin``, you should not specify ``__init__``, instead you use the attribute syntax(?).
     * A subclass of ``DTOMixin`` must be instantiated with keyword arguments.
     * A subclass of ``DTOMixin`` can alternatively be instantiated with keyword arguments in camelCase form.

    For a more detailed explanation of how to use ``DTOMixin``, check the :ref:`data transfer object user guide <dto-user-guide>`.
    """

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        use_enum_values = True
        json_encoders = {
            datetime: isoformat,
            timedelta: timedelta_isoformat,
            ServiceInterface: lambda i: 'hello',
        }

    def dto(self, **kwargs):
        return self.dict(
                exclude_defaults=True,
                exclude_none=True,
                by_alias=True,
                **kwargs,
        )

    def json(
            self,
            exclude_defaults=True,
            exclude_none=True,
            by_alias=True,
            **kwargs
    ) -> str:
        return super().json(
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                by_alias=by_alias,
                **kwargs,
        )
