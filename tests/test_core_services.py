from httmock import HTTMock, urlmatch, response
from arrowhead_client.core_services import all_core_services


def test_register():
    with HTTMock(register_mock):
        all_core_services['register'].consume(
                json={'dummy': 'data'}, cert=('cert.crt', 'key.key')
        )


def test_unregister():
    with HTTMock(unregister_mock):
        all_core_services['unregister'].consume(
                params={'dummy': 'data'}, cert=('cert.crt', 'key.key')
        )


def test_orchestration():
    with HTTMock(orchestration_mock):
        response = all_core_services['orchestration-service'].consume(
                json={'dummy': 'data'}, cert=('cert.crt', 'key.key')
        )


# TODO: Implement tests for the other core services

@urlmatch(netloc='127.0.0.1:8443', path='/serviceregistry/register', method='POST')
def register_mock(url, request):
    return response(content={'dummy': 'data'})


@urlmatch(netloc='127.0.0.1:8443', path='/serviceregistry/unregister', method='DELETE')
def unregister_mock(url, request):
    return {'status': 'OK'}


@urlmatch(netloc='127.0.0.1:8441', path='/orchestrator/orchestration', method='POST')
def orchestration_mock(url, request):
    return response(content={'dummy': 'data'})


@urlmatch(netloc='127.0.0.1:8443', path='/authorization/publickey')
def publickey_mock(url, request):
    return response(content='texttexttext')
