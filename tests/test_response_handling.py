from arrowhead_client import core_service_responses as csr


def test_registration_response():
    csr.handle_service_register_response({'dummy': 'data'})


def test_single_orchestration_response():
    orchestrator_response = {
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
        }]
    }

    returned_service = csr.handle_orchestration_response(orchestrator_response)

    assert 'test' == returned_service.service_definition
    assert 'test/service' == returned_service.service_uri
    assert 'HTTP-SECURE-JSON' == returned_service.interface
    assert '127.0.0.1' == returned_service.address
    assert 3456 == returned_service.port


def test_multiple_orchestration_response():
    orchestrator_response = {
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

    returned_service = csr.handle_orchestration_response(orchestrator_response)

    assert 'test' == returned_service.service_definition
    assert 'test/service' == returned_service.service_uri
    assert 'HTTP-SECURE-JSON' == returned_service.interface
    assert '127.0.0.1' == returned_service.address
    assert 3456 == returned_service.port


def test_empty_orchestration_response():
    orchestration_response = {"response": []}

    returned_service = csr.handle_orchestration_response(orchestration_response)
