import arrowhead_client.client.core_service_forms.client
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service, ServiceInterface
import arrowhead_client.client.core_service_forms.client as forms

requester_system = ArrowheadSystem.make('test_system', 'localhost', 0)
provider_system = ArrowheadSystem.make('test_system', 'localhost', 0)
provided_service = Service(
        service_definition='test_service',
        service_uri='/test/test/test',
        interface=ServiceInterface('HTTP', 'SECURE', 'JSON'),
        access_policy='CERTIFICATE',
        metadata={'dummy': 'data'},
        version=0,
)


def test_registration_form():
    registration_form = forms.ServiceRegistrationForm.make(
            provided_service=provided_service,
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

    assert valid_keys == registration_form.dto().keys()

def test_orchestration_flags():
    valid_keys = {
        'matchmaking',
        'metadataSearch',
        'onlyPreferred',
        'pingProviders',
        'overrideStore',
        'enableInterCloud',
        'triggerInterCloud',
    }

    of = arrowhead_client.client.core_service_forms.client.OrchestrationFlags.make(*([True] * 7))

    assert set(of.dto().keys()) == valid_keys
    assert of.override_store == True


def test_orchestration_form():
    orchestration_flags = forms.OrchestrationFlags(matchmaking=True)
    orchestration_form = forms.OrchestrationForm.make(
            requester_system,
            provided_service,
            orchestration_flags,
            {'test': 'test'},
    )

    valid_keys = {
        'requesterSystem',
        'requestedService',
        'preferredProviders',
        'orchestrationFlags',
    }

    assert set(orchestration_form.dto().keys()) == valid_keys
