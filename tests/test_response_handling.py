import pytest
import json
from contextlib import nullcontext

from arrowhead_client.client import core_service_responses as csr
from arrowhead_client.response import Response
from arrowhead_client import errors
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem


@pytest.fixture
def error_response(request) -> Response:
    error_code = request.param
    return Response(b'{"errorMessage": "test"}', 'JSON', error_code,)


class TestErrorHandler:
    @pytest.mark.parametrize('error_response, expectation', [
            (200, nullcontext()),
            (401, pytest.raises(errors.NotAuthorizedError)),
            (500, pytest.raises(errors.CoreServiceNotAvailableError)),
        ], indirect=['error_response']
    )
    def test_common_error_handler(self, error_response, expectation):
        @csr.core_service_error_handler
        def process_some_service(response):
            pass

        with expectation:
            process_some_service(error_response)


class TestServiceRegistry:

    @pytest.fixture
    def query_result(self, query_response):
        query_data = query_response.read_json()['serviceQueryData'][0]
        service = Service(
                query_data['serviceDefinition']['serviceDefinition'],
                query_data['serviceUri'],
                query_data['interfaces'][0]['interfaceName'],
                query_data['secure'],
                query_data['metadata'],
                query_data['version'],
        )

        system = ArrowheadSystem.from_dto(query_data['provider'])

        return service, system

    def test_good_query_response(self, query_response, query_result):
        true_service, true_system = query_result

        test_list = csr.process_service_query(query_response)
        test_service, test_system = test_list[0]
        assert test_service == true_service
        assert test_system == true_system

    def test_bad_query_response(self):
        bad_response = Response(b'{"errorMessage": "Could not query Service Registry"}', 'JSON', 400,)

        with pytest.raises(errors.CoreServiceInputError):
            csr.process_service_query(bad_response)

    @pytest.mark.parametrize('error_response, expectation', [
        (400, pytest.raises(errors.CoreServiceInputError)),
    ], indirect=['error_response'])
    def test_registration_response(self, error_response, expectation):
        with expectation:
            csr.process_service_register(error_response)

    @pytest.mark.parametrize('error_response, expectation', [
        (400, pytest.raises(errors.CoreServiceInputError)),
    ], indirect=['error_response'])
    def test_unregistration_response(self, error_response, expectation):
        with expectation:
            csr.process_service_unregister(error_response)


class TestOrchestrator:
    def test_orchestration_response(self, orchestration_data):
        orchestrator_response = Response(json.dumps(orchestration_data).encode(), 'JSON', 200,)

        orchestration_rules = csr.process_orchestration(orchestrator_response, 'GET')
        assert len(orchestration_rules) == len(orchestration_data['response'])

        first_rule = orchestration_rules[0]

        assert first_rule.service_definition == 'test'
        assert first_rule.endpoint == '127.0.0.1:3456/test/provided_service'
        assert first_rule.method == 'GET'
        assert first_rule.authorization_token == 'h983u43h9834p'
        assert first_rule.access_policy == 'TOKEN'

    def test_bad_orchestration_response(self):
        orchestrator_response = Response(b'{"errorMessage": ""}', 'JSON', 400)

        with pytest.raises(errors.OrchestrationError):
            orchestration_rules = csr.process_orchestration(orchestrator_response, 'GET')

    def test_empty_orchestration_response(self):
        orchestration_response = Response(b'{"response": []}', 'JSON', 200,)

        handled_responses = csr.process_orchestration(orchestration_response)

        assert handled_responses == []

class TestAuthorization:
    def test_publickey(self, publickey_response, publickey_true):
        test_publickey = csr.process_publickey(publickey_response)
        assert test_publickey == publickey_true



@pytest.fixture
def query_response():
    return Response(
            json.dumps({'serviceQueryData': [
                {
                    'id': 317,
                    'serviceDefinition': {
                        'id': 6,
                        'serviceDefinition': 'orchestration-service',
                        'createdAt': '2020-06-11 09:13:15',
                        'updatedAt': '2020-06-11 09:13:15'
                    },
                    'provider': {
                        'id': 6,
                        'systemName': 'orchestrator',
                        'address': 'orchestrator',
                        'port': 8441,
                        'authenticationInfo': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyjsF7BBDoSL8KEdAdTo3LlCAwYWsjY75gVVFY51AdqOwWNfMYu0PrC+xgrH/DjZFOgo8R1E3GfbNBDGhrn35PZpoQUYbMhM1ZTs38xbAUKTMp829OiORHHtRQlAg2znWETcOyTZPU++/fKnMsCwVrlRo78vQhAghB3X9FkUH5uUsgS61uTh77NhiX6xbqaH+48WHy9iOgo98+gYNZIINte9DBoMiaPzp0wY3puNX+TxAuAkKnNMfJka3pRM3rlrlHiAnzT80uOoisFpu7DF/ySqfZOR+SbZ/uMJWxBtARfPxWuBLRnXY1LtiLMfKuf7gkvemo10KsNiWU8o9iLEfAQIDAQAB',
                        'createdAt': '2020-06-11 09:13:15',
                        'updatedAt': '2020-12-04 15:04:12'
                    },
                    'serviceUri': '/orchestrator/orchestration',
                    'secure': '',
                    'version': 1,
                    'interfaces': [
                        {
                            'id': 1,
                            'interfaceName': 'HTTP-SECURE-JSON',
                            'createdAt': '2020-06-11 06:44:44',
                            'updatedAt': '2020-06-11 06:44:44'
                        }
                    ],
                    'createdAt': '2020-12-13 17:52:45',
                    'updatedAt': '2020-12-13 17:52:45',
                    'metadata': {'dummy': 'data'},
                    'endOfValidity': '2020-02-20',
                }
            ], 'unfilteredHits': 1}).encode(),
            'JSON',
            200,
    )

@pytest.fixture
def orchestration_data():
    return {
        "response": [{
            "provider": {
                "id": 1,
                "systemName": "test_provider",
                "address": "127.0.0.1",
                "port": 3456,
                "authenticationInfo": "",
                "createdAt": "string",
                "updatedAt": "string"},
            "service": {
                "id": 1,
                "serviceDefinition": "test",
                "createdAt": "string",
                "updatedAt": "string"},
            "serviceUri": "test/provided_service",
            "secure": "TOKEN",
            "metadata": {},
            "interfaces": [{
                "id": 1,
                "createdAt": "string",
                "interfaceName": "HTTP-SECURE-JSON",
                "updatedAt": "string"}
            ],
            "version": 0,
            "authorizationTokens": {"HTTP-SECURE-JSON": "h983u43h9834p"},
            "warnings": []
        }, {
            "provider": {
                "id": 2,
                "systemName": "test_provider_2",
                "address": "127.0.0.1",
                "port": 3457,
                "authenticationInfo": "",
                "createdAt": "string",
                "updatedAt": "string"},
            "service": {
                "id": 2,
                "serviceDefinition": "test",
                "createdAt": "string",
                "updatedAt": "string"},
            "serviceUri": "test/provided_service",
            "secure": "CERTIFICATE",
            "metadata": {},
            "interfaces": [{
                "id": 2,
                "createdAt": "string",
                "interfaceName": "HTTP-SECURE-JSON",
                "updatedAt": "string"}
            ],
            "version": 1,
            "authorizationTokens": {},
            "warnings": []},
        ]
    }
@pytest.fixture
def der_publickey():
    der_string = b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAm3JnFI/O7kHWbaOiBVSK\n' \
                 b'MYx5LDYUbL1RQp/0GFAtWadf+2N1C9dKXSV19E0k0zUA3GJJZg8h6K6U8pG2JRaF\n' \
                 b'Adm+/LcgL1A5GM6juGC1RGlUBGXK+I84cvH0jRnYy9x21+1quZmEyF1AXyxQjrCD\n' \
                 b'ADeIsIJnWxKHeL7Exb4DbIag1xZNIzLoyPIiEjjM5YNuT6ntSbdzys5vVrcshgbS\n' \
                 b'6sBPZx5CYrAN2rI4OUA2kaz1jnbQk3o8fWGLU2Rb4bE4aW4+ol6xc+aeCcOSVUeH\n' \
                 b'1ePPeG5c/B0Q0m23uGXSzVGmyWuxDALkdWWtLvMzdWu0CzzoqBFTYWPsxEb0rT3e\n' \
                 b'LQIDAQAB'

    return der_string

@pytest.fixture
def publickey_true(der_publickey):
    return f'-----BEGIN PUBLIC KEY-----\n' \
           f'{der_publickey.decode()}\n' \
           f'-----END PUBLIC KEY-----\n'


@pytest.fixture
def publickey_response(der_publickey) -> Response:
    return Response(der_publickey, 'JSON', 200,)