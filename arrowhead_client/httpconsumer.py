from typing import Dict, Union

import requests as backend
from arrowhead_client.abc import BaseConsumer

class HttpSecureConsumer(BaseConsumer):
    """ Interface for consumer code """

    def consume_service(self, service_uri: str, method: str, **kwargs) -> backend.Response:
        """ Consume registered service """
        # TODO: Add error handling for the case where the service is not
        # registered in _consumed_services
        service_uri = https: + service_uri

        service_response = backend.request(method, service_uri, verify=False, **kwargs)

        return service_response

    def extract_payload(
            self,
            service_response: backend.Response,
            payload_type: str) -> Union[Dict, str]:
        if payload_type.upper() == 'JSON':
            return service_response.json()

        return service_response.text

