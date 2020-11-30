from base64 import b64encode, b64decode
from typing import Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

# TODO: Implement this https://blog.cyberreboot.org/using-pkcs-12-formatted-certificates-in-python-fd98362f90ba to reduce file io and use pkcs12

def cert_cn(cert_string: str) -> str:
    cert = x509.load_pem_x509_certificate(cert_string.encode(), default_backend())
    subject = cert.subject
    _, common_name = subject.rfc4514_string().split('=')
    return common_name


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