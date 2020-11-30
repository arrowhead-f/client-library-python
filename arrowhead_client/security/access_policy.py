"""
Access Policy module
"""
import json
import time
from typing import Tuple

from cryptography.hazmat.primitives import serialization
from jwcrypto import jwk, jwt

from arrowhead_client.abc import AccessPolicy
from arrowhead_client.security.utils import RSAPrivateKey, RSAPublicKey
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem


class TokenAccessPolicy(AccessPolicy):
    """
    Access policy used when :code:`TOKEN` is specified.

    Attributes:
        authorization_key: Public key of the Authorization system in the local cloud.
    """
    def __init__(self, authorization_key: RSAPublicKey = None, **kwargs) -> None:
        self.authorization_key = authorization_key or kwargs.get('authorization_key')

    def is_authorized(self,
                      consumer_cn: str,
                      provider: ArrowheadSystem,
                      provided_service: Service,
                      token: str,
                      **kwargs, ) -> Tuple[bool, str]:
        token = AccessToken.from_string(token, provider._privatekey, self.authorization_key)
        is_valid = consumer_cn.startswith(token.consumer_id) and \
                   provided_service.interface == token.interface_id and \
                   provided_service.service_definition == token.service_id
        if not is_valid:
            return is_valid, 'Invalid token'
        return is_valid, ''


class CertificateAccessPolicy(AccessPolicy):
    """
    Access policy used when :code:`CERTIFICATE` is specified.
    """
    def __init__(self, **kwargs):
        pass

    def is_authorized(self,
                      consumer_cn: str,
                      provider: ArrowheadSystem,
                      provided_service: Service,
                      token: str,
                      **kwargs, ) -> Tuple[bool, str]:
        if not consumer_cn:
            return False, ''
        return True, ''


class UnrestrictedAccessPolicy(AccessPolicy):
    """
    Access policy used when :code:`NOT_SECURE` is specified.

    This access policy should only be used in development.
    """
    def __init__(self, **kwargs):
        pass

    def is_authorized(self,
                      consumer_cn: str,
                      provider: ArrowheadSystem,
                      provided_service: Service,
                      token: str,
                      **kwargs, ) -> Tuple[bool, str]:
        return True, ''


def get_access_policy(policy_name: str, **kwargs) -> AccessPolicy:
    """Factory function for access policies"""
    if policy_name == 'NOT_SECURE':
        return UnrestrictedAccessPolicy(**kwargs)
    elif policy_name == 'CERTIFICATE':
        return CertificateAccessPolicy(**kwargs)
    elif policy_name == 'TOKEN':
        return TokenAccessPolicy(**kwargs)
    else:
        raise ValueError(
            f'{policy_name} is not a valid access policy. Valid policies are {{NOT_SECURE, CERTIFICATE, TOKEN}}')


class AccessToken:
    """
    Data container for the token used with the token access policy

    Attributes:
        consumer_id: Consumer CN
        interface_id: Provided service interface description
        service_id: Provided service definition
    """
    def __init__(self,
                 consumer_id: str,
                 interface_id: str,
                 service_id: str, ) -> None:
        self.consumer_id = consumer_id
        self.interface_id = interface_id
        self.service_id = service_id

    @classmethod
    def from_string(cls,
                    auth_string: str,
                    privatekey: RSAPrivateKey,
                    authorization_key: RSAPublicKey) -> 'AccessToken':
        """
        Creates an AccessToken from the given authorization header.

        Args:
            auth: the AUTHORIZATION string.
            privatekey: Provider private key.
            authorization_key: Authorization system public key.
        Returns:
            An AccessToken constructed from the information in the authentication header.
        Raises:
            ValueError: Malformed authorization header.
            RuntimeError: Invalid token claims.
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
