import pytest
import time
from contextlib import nullcontext

import arrowhead_client.security.access_policy as ap
from arrowhead_client.service import Service
from arrowhead_client import constants
from tests.test_security.test_access_token import generate_claims
from tests.test_security import conftest

def pytest_generate_tests(metafunc):
    # called once per each test function
    if metafunc.cls.__name__ == 'TestGetAccessPolicy':
        return
    if metafunc.function.__name__ == 'test_bad_consumer_cert':
        funcarglist = metafunc.cls.params[metafunc.function.__name__]
        argnames = ['token_test_variables', 'access_policy_service', 'response']
        metafunc.parametrize(
                argnames,
                [[funcargs['claims'], funcargs['bad_claims'], funcargs['response']]
                 for funcargs in funcarglist],
                indirect=['token_test_variables', 'access_policy_service']
        )
    else:
        funcarglist = metafunc.cls.params[metafunc.function.__name__]
        argnames = ['token_test_variables', 'access_policy_service', 'response']
        metafunc.parametrize(
                argnames,
                [[funcargs['claims'], funcargs['claims'], funcargs['response']]
                 for funcargs in funcarglist],
                indirect=['token_test_variables', 'access_policy_service']
)


class TestTokenAccessPolicy:
    now = time.time()

    cid = 'pytest'
    sid = 'pytest'
    iid = 'HTTP-SECURE-JSON'
    params = {
        'test_valid_token': [{
            'claims': generate_claims('39hu209cp239c', 'Authorization', now - 200, now - 300, cid, sid, iid, now + 2000),
            'response': True
        }],
        'test_malformed_auth_string': [{
            'claims': generate_claims('93pc239pc203', 'Authorization', now - 2000, now - 300, cid, sid, iid, now + 3000),
            'response': False
        }],
        'test_invalid_claims': [{
            'claims': generate_claims('93pc239pc203', 'Authorization', now + 2000, now - 300, cid, sid, iid, now + 3000),
            'response': False
        }, {
            'claims': generate_claims('93pc239pc203', 'Authorization', now - 2000, now + 300, cid, sid, iid, now + 3000),
            'response': False
        }, {
            'claims': generate_claims('93pc239pc203', 'auth', now - 2000, now - 300, cid, sid, iid, now + 3000),
            'response': False
        }, {
            'claims': generate_claims('93pc239pc203', 'Authorization', now - 2000, now - 300, cid, sid, iid, now - 3000),
            'response': False
        }],
        'test_bad_provider_information': [{
            'claims': generate_claims('39hu209cp239c', 'Authorization', now - 200, now - 300, cid, sid, iid, now + 2000),
            'response': False
        }],
       'test_bad_consumer_cert' : [{
           'claims': generate_claims('39hu209cp239c', 'Authorization', now - 200, now - 300, cid, sid, iid, now + 2000),
           'bad_claims': generate_claims('39hu209cp239c', 'Authorization', now - 200, now - 300, 'bad_consumer', sid, iid, now + 2000),
           'response': False
       }]
    }

    def test_valid_token(self, token_test_variables, access_policy_service, response):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.TokenAccessPolicy(provided_service, provider_keyfile, auth_info=a_pub_key)

        assert test_policy.is_authorized(consumer_cert_str, auth_string) == response

    @pytest.mark.parametrize('invalid_auth_string', conftest.INVALID_AUTH_LIST)
    def test_malformed_auth_string(self, token_test_variables, access_policy_service, response, invalid_auth_string):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.TokenAccessPolicy(provided_service, provider_keyfile, auth_info=a_pub_key)

        assert test_policy.is_authorized(consumer_cert_str, invalid_auth_string) == response

    def test_invalid_claims(self, token_test_variables, access_policy_service, response):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.TokenAccessPolicy(provided_service, provider_keyfile, auth_info=a_pub_key)

        assert test_policy.is_authorized(consumer_cert_str, auth_string) == response

    @pytest.mark.parametrize('bad_provider', [
        Service(sid, 'pytest', 'HTTP-INSECURE-XML'),
        Service(sid, 'pytest', 'NON-CONFORMING-FORMAT'),
        Service('bad_provider', 'pytest', iid),
        Service('bad_provider', 'pytest', 'COAP-INSECURE-XML')
    ])
    def test_bad_provider_information(self, token_test_variables, access_policy_service, response, bad_provider):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.TokenAccessPolicy(bad_provider, provider_keyfile, auth_info=a_pub_key)

        assert test_policy.is_authorized(consumer_cert_str, auth_string) == response

    def test_bad_consumer_cert(self, token_test_variables, access_policy_service, response):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, bad_consumer_cert_str = access_policy_service

        test_policy = ap.TokenAccessPolicy(provided_service, provider_keyfile, auth_info=a_pub_key)

        assert test_policy.is_authorized(bad_consumer_cert_str, auth_string) == response

class TestCertificateAccessPolicy:
    now = time.time()

    jti = '39hu209cp239c'
    iss = 'Authorization'
    cid = 'pytest'
    sid = 'pytest'
    iid = 'HTTP-SECURE-JSON'
    params = {
        'test_valid_cert': [{
            'claims': generate_claims(jti, iss, now - 200, now - 300, cid, sid, iid, now + 2000),
            'response': True
        }],
        'test_invalid_cert': [{
            'claims': generate_claims(jti, iss, now - 200, now - 300, cid, sid, iid, now + 2000),
            'response': False
        }],
    }

    def test_valid_cert(self, token_test_variables, access_policy_service, response):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.CertificateAccessPolicy()

        assert test_policy.is_authorized(consumer_cert_str, auth_string) == response

    @pytest.mark.parametrize('bad_cert', ['qwertyuiopasdfghjklzxcvbnm'])
    def test_invalid_cert(self, token_test_variables, access_policy_service, response, bad_cert):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.CertificateAccessPolicy()

        # TODO: fix CertificateAccessPolicy and make this test do something again
        #assert test_policy.is_authorized(bad_cert, auth_string) == response


class TestUnrestrictedAccessPolicy:
    now = time.time()

    cid = 'pytest'
    sid = 'pytest'
    iid = 'HTTP-SECURE-JSON'
    params = {
        'test_unrestricted_policy': [{
            'claims': generate_claims('39hu209cp239c', 'Authorization', now - 200, now - 300, cid, sid, iid, now + 2000),
            'response': True
        }]
    }

    @pytest.mark.parametrize('random_str', ['notentoheur', 'llllellellell', b'enthoenuh'])
    def test_unrestricted_policy(self, token_test_variables, access_policy_service, response, random_str):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables
        provided_service, consumer_cert_str = access_policy_service

        test_policy = ap.UnrestrictedAccessPolicy()

        assert test_policy.is_authorized(random_str, random_str) == True


class TestGetAccessPolicy:
    @pytest.fixture(scope='class')
    def policy_input(self):
        service = Service(
                'pytest',
                'test',
                'HTTP-SECURE-JSON',
        )

        dummy_private, dummy_public = conftest.generate_keys()
        return service, dummy_private, dummy_public

    @pytest.mark.parametrize('input_name, true_class, expectation',
        list(zip(
                [constants.AccessPolicy.UNRESTRICTED, constants.AccessPolicy.CERTIFICATE, constants.AccessPolicy.TOKEN, 'WRONG_NAME', 1234],
                [ap.UnrestrictedAccessPolicy, ap.CertificateAccessPolicy, ap.TokenAccessPolicy, None, None],
                [nullcontext()]*3 + [pytest.raises(ValueError)]*2,
        ))
    )
    def test_input(self, input_name, policy_input, true_class, expectation):
        dummy_service, dummy_private, dummy_public = policy_input
        with expectation:
            access_policy = ap.get_access_policy(
                    input_name,
                    dummy_service,
                    dummy_private,
                    authorization_key=dummy_public
            )
            assert isinstance(access_policy, true_class)
