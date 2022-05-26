import pytest

import arrowhead_client.dto


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