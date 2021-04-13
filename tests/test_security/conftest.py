import pytest
import base64
import datetime
from collections import namedtuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import NameOID
from jwcrypto import jwk, jwt

from arrowhead_client.service import Service


def generate_cert(common_names, private_key, public_key):
    if not isinstance(common_names, list):
        common_names = [common_names]
    cn_attributes = [x509.NameAttribute(NameOID.COMMON_NAME, cn) for cn in common_names if cn is not None]
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'PYTEST'),
        *cn_attributes
    ])

    cert = x509.CertificateBuilder().subject_name(
            subject
    ).issuer_name(
            issuer
    ).public_key(
            public_key
    ).serial_number(
            x509.random_serial_number()
    ).not_valid_before(
            datetime.datetime.utcnow()
    ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
    ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName('localhost')]),
            critical=False
    ).sign(private_key, hashes.SHA256(), backend=default_backend())

    return cert


def generate_keys():
    private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
    )

    public_key = private_key.public_key()

    return private_key, public_key


@pytest.fixture
def provider_variables(request, tmp_path_factory):
    private_key, public_key = generate_keys()

    if hasattr(request, 'param'):
        common_names = request.param
    else:
        common_names = 'test.utils'

    cert = generate_cert(common_names, private_key, public_key)

    tmp_dir = tmp_path_factory.mktemp('temp')
    keyfile = tmp_dir / 'cert.key'
    certfile = tmp_dir / 'cert.crt'

    with open(keyfile, 'wb') as kf:
        kf.write(
                private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption()
                )
        )
    with open(certfile, 'wb') as cf:
        cf.write(cert.public_bytes(
                encoding=serialization.Encoding.PEM
        )
        )
    authentication_info = base64.b64encode(
            public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
    ).decode()

    variables = ProviderVariables(
            private_key,
            public_key,
            cert,
            common_names,
            keyfile,
            certfile,
            authentication_info
    )
    return variables


ProviderVariables = namedtuple(
        'ProviderVariables',
        [
            'private_key',
            'public_key',
            'cert',
            'common_name',
            'keyfile',
            'certfile',
            'authentication_info',
        ]
)


@pytest.fixture
def token_test_variables(request, tmp_path):
    provider_private_key, _ = generate_keys()

    authorization_private_key, authorization_public_key = generate_keys()

    provider_private_jwk = jwk.JWK.from_pem(
            provider_private_key.private_bytes(  # type:ignore
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
            )
    )
    authorization_private_jwk = jwk.JWK.from_pem(
            authorization_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
            )
    )

    encryption_header = {"alg": "RSA-OAEP-256", "enc": "A256CBC-HS512", "cty": "JWT"}
    sign_header = {"alg": "RS512"}
    claims = request.param

    signed_token = jwt.JWT(header=sign_header, claims=claims)
    signed_token.make_signed_token(authorization_private_jwk)
    encrypted_token = jwt.JWT(header=encryption_header, claims=signed_token.serialize())
    encrypted_token.make_encrypted_token(provider_private_jwk)

    provider_keyfile = tmp_path / 'provider.key'
    with open(provider_keyfile, 'wb') as keyfile:
        keyfile.write(provider_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    auth_authorization_info = authorization_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    auth_string = f'Bearer {encrypted_token.serialize()}'
    return auth_string, provider_keyfile, auth_authorization_info, claims


@pytest.fixture
def access_policy_service(request):
    claims = request.param

    consumer_private_key, consumer_public_key = generate_keys()
    consumer_cert = generate_cert(claims['cid'], consumer_private_key, consumer_public_key)
    consumer_cert_string = consumer_cert.public_bytes(
            encoding=serialization.Encoding.PEM,
    ).decode()

    service_definition = claims['sid']
    service_interface = claims['iid']

    service = Service(
            service_definition,
            'pytest/access',
            service_interface,
    )

    return service, consumer_cert_string


INVALID_AUTH_LIST = [
    'bearer <TOKEN>',
    '<TOKEN>',
    'Bearer<TOKEN>',
    'Bearer <TOKEN> reraeB',
]
