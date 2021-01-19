import pytest
from contextlib import nullcontext

from cryptography.hazmat.primitives import serialization

from arrowhead_client.security import utils
from arrowhead_client import errors


def public_serialization(public_key) -> bytes:
    return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def private_serialization(private_key):
    return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
    )


def test_cert_cn(provider_variables):
    *_, common_name, _, certfile, _, = provider_variables

    with open(certfile, 'rb') as cf:
        test_cn = utils.cert_cn(cf.read().decode())

    assert test_cn == common_name


@pytest.mark.parametrize('provider_variables, expectation', [
    (None, pytest.raises(RuntimeError)),
    ('', pytest.raises(RuntimeError)),
    (['test', 'pytest'], pytest.raises(RuntimeError)),
    (['pytest'], nullcontext()),
    ('pytest', nullcontext()),
], indirect=['provider_variables'])
def test_cert_cn_bad_names(provider_variables, expectation):
    *_, common_name, _, certfile, _, = provider_variables

    with expectation:
        with open(certfile, 'rb') as cf:
            test_cn = utils.cert_cn(cf.read().decode())


def test_extract_cert(provider_variables):
    _, _, cert, *_, certfile, _, = provider_variables

    test_cert = utils.extract_cert(certfile)

    assert test_cert == cert


def test_extract_publickey(provider_variables):
    _, public_key, *_, certfile, _, = provider_variables

    test_public_key = utils.extract_publickey(certfile)

    public_key_serial = public_serialization(public_key)

    test_key_serial = public_serialization(test_public_key)

    assert test_key_serial == public_key_serial


def test_extract_empty_publickey():
    test_public_key = utils.extract_publickey('')

    assert test_public_key is None


def test_create_authentication_info(provider_variables):
    _, public_key, *_, authentication_info = provider_variables

    test_authentication_info = utils.create_authentication_info(public_key)

    assert test_authentication_info == authentication_info


def test_create_empty_authentication_info():
    test_authentication_info = utils.create_authentication_info(None)

    assert test_authentication_info == ''


def test_der_to_pem(provider_variables):
    _, public_key, *_, authentication_info = provider_variables

    test_public_serial = utils.der_to_pem(authentication_info)

    public_key_serial = public_serialization(public_key).decode()

    assert test_public_serial == public_key_serial


def test_cert_to_authentication_info(provider_variables):
    *_, certfile, authentication_info = provider_variables

    test_authentication_info = utils.cert_to_authentication_info(certfile)

    assert test_authentication_info == authentication_info
