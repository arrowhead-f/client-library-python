import json
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from jwcrypto import jwk, jwt


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