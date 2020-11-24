from typing import Dict, Union

import requests
from arrowhead_client.abc import BaseConsumer
from arrowhead_client.service import Service
from arrowhead_client.response import Response
from arrowhead_client.system import ArrowheadSystem


class HttpConsumer(BaseConsumer):
    """ Interface for consumer code """

    def consume_service(self,
                        service: Service,
                        system: ArrowheadSystem,
                        method: str,
                        token: str,
                        **kwargs) -> Response:
        """ Consume registered service """
        # TODO: Add error handling for the case where the service is not
        # registered in _consumed_services

        service_uri = service.service_uri
        payload_type = service.interface.payload

        # Check if cert- and keyfiles are given and use tls if they are.
        if any(kwargs['cert']):
            service_url = f'https://{system.authority}/{service_uri}'
        else:
            service_url = f'http://{system.authority}/{service_uri}'

        service_response = requests.request(method,
                                            service_url,
                                            verify=False,
                                            auth=ArrowheadAuth(token),
                                            **kwargs
        )

        if payload_type == 'JSON':
            print(service_response.text)
            return Response(service_response.json(), 'JSON', service_response.status_code, '')
        elif payload_type == 'TEXT':
            return Response(service_response.text, 'TEXT', service_response.status_code, '')

        return Response(service_response.content, 'bytes', service_response.status_code, '')

    def extract_payload(
            self,
            service_response: Response,
            payload_type: str) -> Union[Dict, str]:
        """
        if payload_type.upper() == 'JSON':
            return service_response.json()

        return service_response.text
        """
        # TODO: See if this method is still useful
        return {}

class ArrowheadAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: requests.Request):
        if self.token:
            r.headers['Authorization'] = f'Bearer {self.token}'

        return r

