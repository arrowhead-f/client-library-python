#!/usr/bin/env python

import unittest
from arrowhead_client.arrowhead_system import ExternalSystem
import arrowhead_client.core_service_forms as forms

class TestForms(unittest.TestCase):

    """Form Tests"""

    def setUp(self):
        self.test_system = ExternalSystem(
                'test',
                'localhost',
                '2345',
                '')

    def tearDown(self):
        pass

    def test_base_service_form_wont_instantiate(self):
        with self.assertRaises(TypeError):
            test = forms.BaseServiceForm()

    def test_core_system_service_form_wont_instantiate(self):
        with self.assertRaises(TypeError):
            test = forms.BaseServiceForm()

    def test_core_system_service_correct_format(self):
        class TestCSSF(forms.CoreSystemServiceForm):
            def __init__(self,
                    something,
                    test_thing,
                    testing_more_stuff):
                self.something = something
                self.test_thing = test_thing
                self.testing_more_stuff = testing_more_stuff

        correct_form = {
                'something': 1,
                'testThing': 'test_thing',
                'testingMoreStuff': 'test_more_stuff'}

        test_cssf_form = TestCSSF(1, 'test_thing', 'test_more_stuff').form

        self.assertEqual(correct_form, test_cssf_form)

    def test_service_query_form(self):
        test_sqf = forms.ServiceQueryForm(
                'test_service',
                'HTTP-SECURE-JSON',
                'SECURE')

        correct_form_keys = set(
                ['serviceDefinitionRequirement',
                'interfaceRequirements',
                'securityRequirements',
                'metadataRequirements',
                'versionRequirement',
                'maxVersionRequirement',
                'minVersionRequirement',
                'pingProviders'])

        test_form_keys = set(test_sqf.form.keys())

        self.assertEqual(correct_form_keys, test_form_keys)

    def test_service_registration_form(self):
        test_srf = forms.ServiceRegistrationForm(
                'test_service',
                'test/test',
                'HTTP-SECURE-JSON',
                'SECURE',
                self.test_system)

        correct_form_keys = set(
                [
                    'serviceDefinition',
                    'serviceUri',
                    'secure',
                    'interfaces',
                    'providerSystem',
                    'metadata',
                    'endOfValidity',
                    'version']
                )

        test_form_keys = set(test_srf.form.keys())

        self.assertEqual(correct_form_keys, test_form_keys)

        def test_orchestration_form(self):
            test_of = forms.OrchestrationForm(
                    self.test_system,
                    'test_service')

            correct_form_keys = set(
                    [
                        'requesterSystem',
                        'requestedService',
                        'orchestrationFlags',
                        'preferredProviders',
                        'commands',
                        'requesterCloud'
                        ]
                    )

            test_form_keys = set(test_of.form.keys())

            self.assertEqual(correct_form_keys, test_form_keys)

if __name__ == "__main__":
    unittest.main()
