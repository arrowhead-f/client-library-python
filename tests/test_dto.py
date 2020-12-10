from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any

import pytest

import arrowhead_client.dto

def test_dto_subclassing():
    @dataclass
    class TestDTO(arrowhead_client.dto.DTOMixin):
        a: Any
        b: Any
        c: Any

    assert TestDTO(1, 2, 3).dto().keys() == {'a', 'b', 'c'}

def test_dto_subclassing_exclude():
    @dataclass
    class TestDTO(arrowhead_client.dto.DTOMixin):
        a: Any
        b: Any
        c: Any

        _dto_excludes = 'c'

    assert TestDTO(1, 2, 3).dto().keys() == {'a', 'b'}

def test_dto_subclassing_property():
    @dataclass
    class TestDTO(arrowhead_client.dto.DTOMixin):
        a: Any
        b: Any

        _dto_property = 'c'

        @property
        def c(self):
            return self.a + self.b

    assert TestDTO(1, 2).dto().keys() == {'a', 'b', 'c'}

@pytest.mark.parametrize('exclude, compare, expectation', (
        (['a'], {'b', 'c', 'abc', 'efg'}, nullcontext()),
        ('', {'a', 'b', 'c', 'abc', 'efg'}, nullcontext()),
        (None, {'a', 'b', 'c', 'abc', 'efg'}, nullcontext()),
        ('d', None, pytest.raises(ValueError)),
        ([1345], None, pytest.raises(ValueError)),
        (1345, None, pytest.raises(TypeError)),
))
def test_dto_exclude(exclude, compare, expectation):
    @dataclass
    class TestDTO(arrowhead_client.dto.DTOMixin):
        a: Any
        b: Any
        c: Any
        abc: Any

        _dto_property = {'efg'}
        @property
        def efg(self):
            return 1

    with expectation:
        test = TestDTO(1, 2, 3, 123)
        assert test.dto(exclude=exclude).keys() == compare




to_snake_case_list = [
    'testingSomeStuff',
    'testWithALarge',
    'TestingPascalCase',
    'TestABCDEFG',
    '_initialUnderscore',
    'trailingUnderscore_']

snake_case_true_list = [
    'testing_some_stuff',
    'test_with_a_large',
    'testing_pascal_case',
    'test_a_b_c_d_e_f_g',
    '_initial_underscore',
    'trailing_underscore_']


@pytest.mark.parametrize('test,expected', zip(to_snake_case_list, snake_case_true_list))
def test_to_snake_case(test, expected):
    test = arrowhead_client.dto.to_snake_case(test)
    assert test == expected


to_camel_case_list = [
    'testing_some_stuff',
    '_test_with_initial_underscore',
    'testing_with__multiple___underscores',
    'test_with_trailing_underscore_']

camel_case_true_list = [
    'testingSomeStuff',
    '_testWithInitialUnderscore',
    'testingWithMultipleUnderscores',
    'testWithTrailingUnderscore_']


@pytest.mark.parametrize('test,expected', zip(to_camel_case_list, camel_case_true_list))
def test_to_camel_case(test, expected):
    test = arrowhead_client.dto.to_camel_case(test)
    assert test == expected