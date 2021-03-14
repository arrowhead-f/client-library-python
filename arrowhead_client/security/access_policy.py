"""
Access Policy module.
=====================

"""
from abc import ABC, abstractmethod
from typing import Any

# Not used because the CertificateAccessPolicy is disabled, see comment there.
from cryptography import x509  # noqa: F401
from cryptography.hazmat.backends import default_backend  # noqa: F401

from arrowhead_client.security.access_token import AccessToken
from arrowhead_client.security.utils import cert_cn
from arrowhead_client.service import Service
from arrowhead_client import errors
from arrowhead_client import constants


class AccessPolicy(ABC):
    """
    Abstract class for access policies.
    """

    @abstractmethod
    def is_authorized(self,
                      consumer_cert_str: str,
                      auth_header: str,
                      **kwargs, ) -> bool:
        """
        Check if consumer is authorized to consume the provided service.

        Returns:
            :code:`True` if authorized, :code:`False` if not authorized or an error occurs.

        """


class TokenAccessPolicy(AccessPolicy):
    """
    Access policy used when :py:enum:member:`~arrowhead_client.constants.AccessPolicy.TOKEN` is specified.

    Args:
        provided_service: Service instance.
        provider_keyfile: Provider keyfile path.
        auth_info: Public key of the Authorization system in the local cloud.
    """

    def __init__(
            self,
            provided_service: Service,
            provider_keyfile: str,
            auth_info: str,
    ) -> None:
        # TODO: don't store a reference to the provided_service, store only the interface and service definition
        self.provided_service = provided_service
        self.provider_keyfile = provider_keyfile
        self.auth_info = auth_info

    def is_authorized(
            self,
            consumer_cert_str: str,
            auth_header: str,
            **kwargs,
    ) -> bool:
        """
        Checks if given token is valid.

        Args:
            consumer_cert_str: PEM certificate string.
            auth_header: String of format :code:`'Bearer <TOKEN>'`.
        Returns:
            ``True`` if valid token, ``False`` if invalid token or error occurs.
        """
        try:
            consumer_cn = cert_cn(consumer_cert_str)
        except ValueError:
            return False

        try:
            token = AccessToken.from_string(
                    auth_header,
                    self.provider_keyfile,
                    self.auth_info
            )
        except errors.InvalidTokenError:
            return False

        is_valid = consumer_cn.startswith(token.consumer_id) and \
                   self.provided_service.interface == token.interface_id and \
                   self.provided_service.service_definition == token.service_id

        return is_valid


class CertificateAccessPolicy(AccessPolicy):
    """
    Access policy used when :py:enum:member:`~arrowhead_client.constants.AccessPolicy.CERTIFICATE` is specified.
    """

    def is_authorized(
            self,
            consumer_cert_str: str,
            *args,
            **kwargs,
    ) -> bool:
        """
        Check valid PEM certificate.

        Args:
            consumer_cert_str: PEM certificate string.
        Returns:
            :code:`True` if given a valid PEM certificate, False otherwise.
        """
        try:
            # TODO: This code is disabled because the certificate is not retrievable when using FastAPI
            # without a reverse proxy, due to the ASGI standard.
            # cert = x509.load_pem_x509_certificate(
            #        consumer_cert_str.encode(),
            #        default_backend()
            # )
            pass
        except ValueError:
            return False

        return True


class UnrestrictedAccessPolicy(AccessPolicy):
    """
    Access policy used when :py:enum:mem:`~arrowhead_client.constants.AccessPolicy.UNRESTRICTED` is specified.

    This access policy should only be used in development.
    """

    def is_authorized(
            self,
            *args,
            **kwargs,
    ) -> bool:
        """
        No checks, always returns :code:`True`

        Returns:
            :code:`True`
        """
        return True


def get_access_policy(
        policy_name: str,
        provided_service: Service,
        privatekey: Any,
        **kwargs) -> AccessPolicy:
    """
    Factory function for access policies.

    Args:
        policy_name: Either :code:`TOKEN`, :code:`CERTIFICATE`, or :code:`UNRESTRICTED`.
        provided_service: Service instance.
        privatekey: Provider keyfile path.
        authorization_key: Authorization core system public key.
    Returns:
        Initialized AccessPolicy instance.
    """
    if policy_name == constants.AccessPolicy.UNRESTRICTED:
        return UnrestrictedAccessPolicy()
    elif policy_name == constants.AccessPolicy.CERTIFICATE:
        return CertificateAccessPolicy()
    elif policy_name == constants.AccessPolicy.TOKEN:
        return TokenAccessPolicy(
                provided_service,
                privatekey,
                kwargs['authorization_key']
        )
    else:
        raise ValueError(
                f'{policy_name} is not a valid access policy.'
                f'Valid policies are {set(policy for policy in constants.AccessPolicy)}'
        )
