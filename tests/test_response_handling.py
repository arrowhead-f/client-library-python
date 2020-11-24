import pytest
from arrowhead_client.client import core_service_responses as csr
from arrowhead_client.response import Response
from arrowhead_client import errors


def test_registration_response():
    with pytest.raises(NotImplementedError) as e:
        csr.handle_service_register_response({'dummy': 'data'})


def test_orchestration_response():
    orchestrator_response_json = {
        "response": [{
            "provider": {
                "id": 0,
                "systemName": "test_provider",
                "address": "127.0.0.1",
                "port": 3456,
                "authenticationInfo": "",
                "createdAt": "string",
                "updatedAt": "string"},
            "service": {
                "id": 0,
                "serviceDefinition": "test",
                "createdAt": "string",
                "updatedAt": "string"},
            "serviceUri": "test/service",
            "secure": "CERTIFICATE",
            "metadata": {},
            "interfaces": [{
                "id": 0,
                "createdAt": "string",
                "interfaceName": "HTTP-SECURE-JSON",
                "updatedAt": "string"}
            ],
            "version": 0,
            "authorizationTokens": {},
            "warnings": []
        }, {
            "provider": {
                "id": 0,
                "systemName": "test_provider_2",
                "address": "127.0.0.1",
                "port": 3457,
                "authenticationInfo": "",
                "createdAt": "string",
                "updatedAt": "string"},
            "service": {
                "id": 0,
                "serviceDefinition": "test",
                "createdAt": "string",
                "updatedAt": "string"},
            "serviceUri": "test/service",
            "secure": "CERTIFICATE",
            "metadata": {},
            "interfaces": [{
                "id": 0,
                "createdAt": "string",
                "interfaceName": "HTTP-SECURE-JSON",
                "updatedAt": "string"}
            ],
            "version": 0,
            "authorizationTokens": {},
            "warnings": []},
        ]
    }
    orchestrator_response = Response(orchestrator_response_json, 'JSON', 200, '')

    handled_responses = csr.process_orchestration_response(orchestrator_response)
    assert len(orchestrator_response_json['response']) == 2
    assert len(handled_responses) == len(orchestrator_response_json['response'])

    (service, system), *_ = handled_responses
    assert 'test' == service.service_definition
    assert 'test/service' == service.service_uri
    assert 'HTTP-SECURE-JSON' == service.interface
    assert 'test_provider' == system.system_name
    assert '127.0.0.1' == system.address
    assert 3456 == system.port
    assert '' == system.authentication_info


def test_empty_orchestration_response():
    orchestration_response = Response({"response": []}, 'JSON', 200, '')

    with pytest.raises(errors.NoAvailableServicesError) as e:
        handled_responses = csr.process_orchestration_response(orchestration_response)

