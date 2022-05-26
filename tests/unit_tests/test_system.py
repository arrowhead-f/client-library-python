import pytest

from cryptography.hazmat.primitives import serialization


from tests.unit_tests.test_security.conftest import generate_keys, generate_cert
from arrowhead_client.system import ArrowheadSystem

@pytest.fixture()
def valid_keys():
    return {
    'systemName',
    'address',
    'port',
    'authenticationInfo'
}

def test_arrowhead_system(valid_keys):
    test_system = ArrowheadSystem.make(
            'test_system',
            '127.0.0.1',
            0,
            'blablabla'
    )

    assert test_system.dto().keys() == valid_keys
    assert test_system.authority == '127.0.0.1:0'
    assert test_system.system_name == 'test_system'
    assert test_system.port == 0

def test_from_dto(valid_keys):
    dto = {
        "systemName": "test_system",
        "address": "127.0.0.1",
        "port": 0,
        "authenticationInfo": "bla"
    }

    test_system = ArrowheadSystem(**dto)

    assert test_system.dto().keys() == valid_keys
    assert test_system.authority == '127.0.0.1:0'
    assert test_system.system_name == 'test_system'
    assert test_system.authentication_info == 'bla'

@pytest.fixture
def certfile_path(tmp_path):
    return tmp_path / 'pytest_cert.crt'

def test_with_certfile(valid_keys, certfile_path):
    priv_key, pub_key = generate_keys()
    cert = generate_cert(['pytest'], priv_key, pub_key)
    with open(certfile_path, 'wb') as cf:
        cf.write(cert.public_bytes(
                encoding = serialization.Encoding.PEM
        ))

    test_system = ArrowheadSystem.with_certfile(
            'test_system',
            '127.0.0.1',
            1337,
            certfile_path,
    )
