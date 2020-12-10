import json

import requests

from arrowhead_client.abc import BaseConsumer
from arrowhead_client.response import Response
from arrowhead_client.configuration import config
from arrowhead_client.rules import OrchestrationRule


class HttpConsumer(BaseConsumer, protocol='HTTP'):
    """ Interface for consumer code """

    def consume_service(self,
                        rule: OrchestrationRule,
                        **kwargs) -> Response:
        """ Consume registered provided_service """
        # TODO: Add error handling for the case where the provided_service is not
        # registered in orchestration_rules
        # TODO: This should be done in client_core.py

        payload_type = rule.payload_type

        # Check if cert- and keyfiles are given and use tls if they are.
        service_url = f'{http(rule.secure)}{rule.endpoint}'

        service_response = requests.request(
                rule.method,
                service_url,
                # TODO: CA should be a parameter of some kind, not part of config
                # TODO: CA should probably be an argument to the consumer
                verify=config['certificate authority'],
                auth=ArrowheadTokenAuth(rule.authorization_token),
                **kwargs
        )
        # TODO: Fix the error handling, it looks like a mess
        if service_response.status_code == 403:
            raise RuntimeError(service_response.text)

        if payload_type == 'JSON':
            try:
                r = Response(service_response.json(), 'JSON', service_response.status_code, '')
            except json.decoder.JSONDecodeError:
                r = Response(service_response.text, 'TEXT', service_response.status_code, '')
            return r
        return Response(service_response.content, 'bytes', service_response.status_code, '')

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

