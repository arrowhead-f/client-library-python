import unittest
from arrowhead_client.system import ArrowheadSystem
import arrowhead_client.core_service_forms as forms

requester_system = ArrowheadSystem('test_system', 'localhost', 0, '')
provider_system = ArrowheadSystem('test_system', 'localhost', 0, '')


def test_registration_form():
    registration_form = forms.ServiceRegistrationForm(
            'test_service',
            '/test',
            'CERTIFICATE',
            ['HTTP-SECURE-JSON'],
            provider_system.dto,
            {'dummy': 'data'},
            'dummy-date',
            0,
    )

    valid_keys = {
        'serviceDefinition',
        'serviceUri',
        'providerSystem',
        'secure',
        'interfaces',
        'metadata',
        'version',
        'endOfValidity',
    }

    assert valid_keys == registration_form.dto.keys()


def test_orchestration_form():
    orchestration_form = forms.OrchestrationForm(
            requester_system.dto,
            'test_service',
            ['HTTP-SECURE-JSON'],
            ['CERTIFICATE'],
            {'dummy': 'data'},
            0,
            0,
            0,
            True,
            {'dummy': True},
            {'dummy': 'data'},
    )

    valid_keys = {
        'requesterSystem',
        'requestedService',
        'preferredProviders',
        'orchestrationFlags',
    }

    assert set(orchestration_form.dto.keys()) == valid_keys
