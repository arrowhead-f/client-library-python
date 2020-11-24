from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service
import arrowhead_client.client.core_service_forms as forms

requester_system = ArrowheadSystem('test_system', 'localhost', 0, '')
provider_system = ArrowheadSystem('test_system', 'localhost', 0, '')


def test_registration_form():
    service = Service(
            service_definition='test_service',
            service_uri='/test/test/test',
            interface='HTTP-SECURE-JSON',
            access_policy='CERTIFICATE',
            metadata={'dummy': 'data'},
            version=0,
    )

    registration_form = forms.ServiceRegistrationForm(
            provided_service=service,
            provider_system=provider_system,
            end_of_validity='dummy-date',
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
    )

    valid_keys = {
        'requesterSystem',
        'requestedService',
        'preferredProviders',
        'orchestrationFlags',
    }

    assert set(orchestration_form.dto.keys()) == valid_keys
