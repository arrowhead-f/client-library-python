from typing import Optional
import json
import time
from dataclasses import dataclass
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives import serialization
from base64 import b64encode, b64decode
#import jwt
from jwcrypto import jwe, jwt, jws, jwk
from authlib.jose import JsonWebEncryption

# TODO: Implement this https://blog.cyberreboot.org/using-pkcs-12-formatted-certificates-in-python-fd98362f90ba to reduce file io and use pkcs12

# TODO: Implement as dataclass?
# TODO: Or maybe as a named tuple?
# @dataclass
class AccessToken:
    def __init__(self,
                 consumer_id: str,
                 interface_id: str,
                 service_id: str, ) -> None:
        self.consumer_id = consumer_id
        self.interface_id = interface_id
        self.service_id = service_id


    @classmethod
    def from_string(cls, auth_string: str, privatekey: RSAPrivateKey, authorization_key: RSAPublicKey) -> 'AccessToken':
        """
        Takes the string of the AUTHORIZATION HTTP header and returns the corresponding token

        Args:
            auth: the AUTHORIZATION string
            privatekey: Provider private key
            authorization_key: Authorization system public key
        """
        bearer, token_string = auth_string.split()

        if bearer != 'Bearer':
            raise ValueError('Malformed authorization header')

        # Generate jwk for private key
        keybytes = privatekey.private_bytes(
                encoding=serialization.Encoding.PEM,
                encryption_algorithm=serialization.NoEncryption(),
                format=serialization.PrivateFormat.PKCS8,
        )
        jwk_privatekey = jwk.JWK.from_pem(keybytes)

        # Generate jwk for public key
        auth_keybytes = authorization_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        jwk_authkey = jwk.JWK.from_pem(auth_keybytes)

        # Decrypt, sign, and extract claims from token
        decrypted_token = jwt.JWT(key=jwk_privatekey, jwt=token_string)
        signed_token = jwt.JWT(key=jwk_authkey, jwt=decrypted_token.claims)
        token_claims = json.loads(signed_token.claims)

        now = time.time()
        if token_claims['iat'] > now:
            raise RuntimeError('JWT not yet issued')
        # TODO: Implement checks for other standard claims.

        new_access_token = cls(
                consumer_id=token_claims['cid'],
                interface_id=token_claims['iid'],
                service_id=token_claims['sid'],
        )

        return new_access_token

def cert_cn(cert_bytes: str) -> str:
    cert = x509.load_pem_x509_certificate(cert_bytes.encode(), default_backend())
    subject = cert.subject
    identifier, common_name = subject.rfc4514_string().split('=')
    return common_name

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
