"""
Access Policy module
"""
from abc import ABC, abstractmethod
from typing import Any

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from arrowhead_client.common import Constants
from arrowhead_client.security.access_token import AccessToken
from arrowhead_client.security.utils import cert_cn
from arrowhead_client.service import Service
from arrowhead_client import errors


class AccessPolicy(ABC):
    """
    Abstract class that describes the interface for access policies.
    """

    @abstractmethod
    def is_authorized(self,
                      consumer_cert_str: str,
                      auth_header: str,
                      **kwargs, ) -> bool:
        """
        Check if consumer is authorized to consume the provided service.

        Args:
            consumer_cert_str: Common name of consumer extracted from the consumer certificate.
            token: Token used with the token access policy.
            kwargs: Possible extra arguments.
        Returns:
            A tuple with a bool value and message string.
            If authorization is successful, the value will be :code:`(True, '')`,
            but if the authorization is unsuccessful value will be :code:`(False, <message>)`,
            where the message will contain information about what went wrong in the
            authorization process.

        """


class TokenAccessPolicy(AccessPolicy):
    """
    Access policy used when :code:`POLICY_TOKEN` is specified.

    Attributes:
        authorization_key: Public key of the Authorization system in the local cloud.
    """
    def __init__(
            self,
            provided_service: Service,
            provider_keyfile: str,
            auth_info: str,
    ) -> None:
        self.provided_service = provided_service
        self.provider_keyfile = provider_keyfile
        self.auth_info = auth_info

    def is_authorized(
            self,
            consumer_cert_str: str,
            auth_header: str,
            **kwargs, ) -> bool:

        consumer_cn = cert_cn(consumer_cert_str)

        try:
            token = AccessToken.from_string(
                    auth_header,
                    self.provider_keyfile,
                    self.auth_info
            )
        except errors.InvalidTokenError:
            # TODO: Log failure
            return False

        is_valid = consumer_cn.startswith(token.consumer_id) and \
                   self.provided_service.interface == token.interface_id and \
                   self.provided_service.service_definition == token.service_id

        return is_valid


class CertificateAccessPolicy(AccessPolicy):
    """
    Access policy used when :code:`POLICY_CERTIFICATE` is specified.
    """

    def is_authorized(self,
                      consumer_cert_str: str,
                      *args,
                      **kwargs, ) -> bool:
        try:
            cert = x509.load_pem_x509_certificate(
                    consumer_cert_str.encode(),
                    default_backend()
            )
        except ValueError:
            return False

        return True


class UnrestrictedAccessPolicy(AccessPolicy):
    """
    Access policy used when :code:`NOT_SECURE` is specified.

    This access policy should only be used in development.
    """

    def is_authorized(self,
                      *args,
                      **kwargs, ) -> bool:
        return True


def get_access_policy(
        policy_name: str,
        provided_service: Service,
        privatekey: Any,
        **kwargs) -> AccessPolicy:
    """Factory function for access policies"""
    if policy_name == Constants.POLICY_UNRESTRICTED:
        return UnrestrictedAccessPolicy()
    elif policy_name == Constants.POLICY_CERTIFICATE:
        return CertificateAccessPolicy()
    elif policy_name == Constants.POLICY_TOKEN:
        return TokenAccessPolicy(
                provided_service,
                privatekey,
                kwargs['authorization_key']
        )
    else:
        raise ValueError(
            f'{policy_name} is not a valid access policy.'
            f'Valid policies are {set(policy for policy in Constants)}'
        )
