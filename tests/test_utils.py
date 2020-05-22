#!/usr/bin/env python

import unittest
from arrowhead_client import utils

class TestUtils(unittest.TestCase):

    """ Test case for utils """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_to_snake_case(self):
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

        for snake_case_test, snake_case_true in zip(
            to_snake_case_list, snake_case_true_list):
            test = utils.to_snake_case(snake_case_test)
            self.assertEqual(test, snake_case_true)

    def test_to_camel_case(self):
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

        for camel_case_test, camel_case_true in zip(
            to_camel_case_list, camel_case_true_list):
            test = utils.to_camel_case(camel_case_test)
            self.assertEqual(test, camel_case_true)

if __name__ == "__main__":
    unittest.main()
