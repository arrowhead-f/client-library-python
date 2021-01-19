from base64 import b64encode, b64decode
from typing import Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


# TODO: Implement this https://blog.cyberreboot.org/using-pkcs-12-formatted-certificates-in-python-fd98362f90ba to reduce file io and use pkcs12

def cert_cn(cert_string: str) -> str:
    cert = x509.load_pem_x509_certificate(
            cert_string.encode(),
            default_backend()
    )
    common_names = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    # TODO: Are these checks necessary anymore?
    if len(common_names) > 1:
        raise RuntimeError('Multiple common names in cert, expected 1.')
    elif len(common_names) == 0:
        raise RuntimeError('No common name in cert, expected 1.')

    common_name = common_names[0].value
    if common_name == '':
        raise RuntimeError('Common name is empty')
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

    return publickey  # type: ignore


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


def der_to_pem(der64: str) -> str:
    publickey = serialization.load_der_public_key(b64decode(der64), backend=default_backend())
    pem_string = publickey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_string.decode()


def cert_to_authentication_info(pem_certfile: str):
    publickey = extract_publickey(pem_certfile)
    authentication_info = create_authentication_info(publickey)

    return authentication_info
