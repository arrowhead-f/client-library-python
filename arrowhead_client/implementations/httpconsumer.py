import requests

from arrowhead_client.abc import BaseConsumer
from arrowhead_client.response import Response
from arrowhead_client.rules import OrchestrationRule


class HttpConsumer(BaseConsumer, protocol='HTTP'):
    """ Interface for consumer code """
    def __init__(self, certificate_authority: str):
        self.certificate_authority = certificate_authority

    def consume_service(self,
                        rule: OrchestrationRule,
                        **kwargs) -> Response:
        """ Consume registered provided_service """

        service_response = requests.request(
                rule.method,
                url=f'{http(rule.secure)}{rule.endpoint}',
                verify=self.certificate_authority,
                auth=ArrowheadTokenAuth(rule.authorization_token),
                **kwargs
        )

        return Response(service_response.content, rule.payload_type, service_response.status_code, '')

def http(secure: str) -> str:
    if secure == 'INSECURE':
        return 'http://'
    return 'https://'

class ArrowheadTokenAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.PreparedRequest):
        if self.token:
            r.headers['Authorization'] = f'Bearer {self.token}'

        return r

