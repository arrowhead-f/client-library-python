import json
import time

from jwcrypto import jwk, jwt  # type: ignore

from arrowhead_client import errors


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
    def from_string(
            cls,
            auth_string: str,
            provider_keyfile: str,
            auth_authorization_info: str,
    ) -> 'AccessToken':
        """
        Creates an AccessToken from the given authorization header.

        Args:
            auth: the AUTHORIZATION string.
            provider_keyfile: Provider keyfile.
            authorization_key: Authorization system public key.
        Returns:
            An AccessToken constructed from the information in the authentication header.
        Raises:
            ValueError: Malformed authorization header.
            RuntimeError: Invalid token claims.
        """
        try:
            bearer, token_string = auth_string.split()
        except ValueError as e:
            raise errors.InvalidTokenError('Malformed authorization header') from e
        except AttributeError as e:
            raise errors.InvalidTokenError from e

        if bearer != 'Bearer':
            raise errors.InvalidTokenError('Malformed authorization header')

        # Generate jwk for provider private key
        with open(provider_keyfile, 'rb') as keyfile:
            jwk_privatekey = jwk.JWK.from_pem(keyfile.read())

        # Generate jwk for authorization public key
        jwk_authkey = jwk.JWK.from_pem(
                auth_authorization_info.encode()
        )

        # Decrypt, sign, and extract claims from token
        decrypted_token = jwt.JWT(key=jwk_privatekey, jwt=token_string)
        try:
            signed_token = jwt.JWT(key=jwk_authkey, jwt=decrypted_token.claims)
        except jwt.JWException as e:
            raise errors.InvalidTokenError from e

        token_claims = json.loads(signed_token.claims)

        now = time.time()
        if token_claims['iat'] > now:
            raise errors.InvalidTokenError('JWT not yet issued')
        if token_claims['iss'] != 'Authorization':
            raise errors.InvalidTokenError('JWT not issued by Authorization system')
        # TODO: Implement checks for other standard claims.

        new_access_token = cls(
                consumer_id=token_claims['cid'],
                interface_id=token_claims['iid'],
                service_id=token_claims['sid'],
        )

        return new_access_token
