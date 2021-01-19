import pytest
import time

from tests.test_security import conftest

from arrowhead_client.security.access_token import AccessToken
from arrowhead_client import errors


def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
            argnames,
            [[funcargs[name] for name in argnames] for funcargs in funcarglist],
            indirect=['token_test_variables']
)

def generate_claims(jti, iss, iat, nbf, cid, sid, iid, exp):
    return dict(jti=jti, iss=iss, iat=iat, nbf=nbf, cid=cid, sid=sid, iid=iid, exp=exp)


class TestAccessToken:
    now = time.time()

    cid = 'pytest'
    sid = 'pytest'
    iid = 'HTTP-SECURE-JSON'
    params = {
        'test_valid_claims': [{
            'token_test_variables': generate_claims('39hu209cp239c', 'Authorization', now - 200, now - 300, cid, sid, iid, now + 2000),
        }],
        'test_malformed_auth_string': [{
            'token_test_variables': generate_claims('93pc239pc203', 'Authorization', now - 2000, now - 300, cid, sid, iid, now + 3000)
        }],
        'test_invalid_claims': [{
            'token_test_variables': generate_claims('93pc239pc203', 'Authorization', now + 2000, now - 300, cid, sid, iid, now + 3000)
        }, {
            'token_test_variables': generate_claims('93pc239pc203', 'Authorization', now - 2000, now + 300, cid, sid, iid, now + 3000)
        }, {
            'token_test_variables': generate_claims('93pc239pc203', 'auth', now - 2000, now - 300, cid, sid, iid, now + 3000 )
        }, {
            'token_test_variables': generate_claims('93pc239pc203', 'Authorization', now - 2000, now - 300, cid, sid, iid, now - 3000)
        }]
    }

    def test_valid_claims(self, token_test_variables):
        auth_string, provider_keyfile, a_pub_key, claims = token_test_variables

        token = AccessToken.from_string(auth_string, provider_keyfile, a_pub_key)

        assert token.consumer_id == claims['cid']
        assert token.service_id == claims['sid']
        assert token.interface_id == claims['iid']

    def test_invalid_claims(self, token_test_variables):
        auth_string, p_priv_key, a_pub_key, claims = token_test_variables

        with pytest.raises(errors.InvalidTokenError):
            token = AccessToken.from_string(auth_string, p_priv_key, a_pub_key)

    @pytest.mark.parametrize('invalid_auth_string',
                             conftest.INVALID_AUTH_LIST
                             )
    def test_malformed_auth_string(self, token_test_variables, invalid_auth_string):
        auth_string, p_priv_key, a_pub_key, claims = token_test_variables

        with pytest.raises(errors.InvalidTokenError):
            auth_string = invalid_auth_string.replace('<TOKEN>', auth_string.split()[1])
            token = AccessToken.from_string(auth_string, p_priv_key, a_pub_key)
