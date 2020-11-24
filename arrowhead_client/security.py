from typing import Optional
from dataclasses import dataclass
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives import serialization
from base64 import b64encode, b64decode
from jose import jwt, jwk
from jose.constants import ALGORITHMS

# TODO: Implement as dataclass?
# TODO: Or maybe as a named tuple?
# @dataclass
class AccessToken:
    def __init__(self, consumer_id, interface_id, service_id):
        self.consumer_id = consumer_id
        self.interface_id = interface_id
        self.service_id = service_id

    @classmethod
    def from_string(cls, token: str, privatekey: RSAPrivateKey, authorization_key: RSAPublicKey):

        return None

class AccessPolicy:
    def __init__(self):
        pass

def extract_cert(certfile: str) -> x509.Certificate:
    with open(certfile, 'rb') as crt:
        # Read certificate from cert file
        cert = x509.load_pem_x509_certificate(
                data=crt.read(),
                backend=default_backend()
        )

    return cert

def extract_publickey(certfile: str) -> Optional[RSAPublicKey]:
    if not certfile:
        return None

    # Get cert
    cert = extract_cert(certfile)

    # Extract RSA public key
    publickey = cert.public_key()
    assert isinstance(publickey, RSAPublicKey)
    # TODO: assert to make mypy happy, needs a cleaner solution

    return publickey

def extract_privatekey(keyfile: str) -> Optional[RSAPrivateKey]:
    if not keyfile:
        return None

    with open(keyfile, 'rb') as key:
        # Read private key from key file
        privatekey = serialization.load_pem_private_key(
                data=key.read(),
                password=None,
                backend=default_backend(),
        )

    return privatekey

def create_authentication_info(publickey: Optional[RSAPublicKey]) -> str:
    if not publickey:
        return ''

    # Get byte encoding for public key
    public_bytes = publickey.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Get string representation of byte64 encoded public key
    return b64encode(public_bytes).decode()

def publickey_from_base64(key64: str) -> RSAPublicKey:
    publickey = serialization.load_der_public_key(
            b64decode(key64),
            default_backend()
    )
    return publickey

def authenticate_token(bearer: str, token: str):
    is_authorized = True

    return is_authorized
