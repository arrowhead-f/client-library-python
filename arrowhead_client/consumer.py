from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Union

import requests as backend
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem as System

@dataclass
class Consumer():
    """ Class to create Arrowhead consumer systems """

    #TODO: Add all arguments instead of using *args
    def __init__(self, keyfile, certfile) -> None:
        self.keyfile = keyfile
        self.certfile = certfile
        self._consumed_services: Dict[str, Tuple[Service, System, str]] = {}

    def consume_service(self, service_definition: str, **kwargs) -> backend.Response:
        """ Consume registered service """
        # TODO: Add error handling for the case where the service is not
        # registered in _consumed_services

        uri, http_method = self._service_uri(service_definition)

        service_response = backend.request(http_method, uri, verify=False, **kwargs)

        return service_response

        #TODO: type ignore above should be removed when mypy issue
        # https://github.com/python/mypy/issues/6799 is fixed

    def _service_uri(self, service_definition: str) -> Tuple[str, str]:
        service, system, http_method = self._consumed_services[service_definition]
        uri = f'https://{system.authority}/{service.service_uri}'

        return uri, http_method

    def _extract_payload(self, service_response, interface) -> Union[Dict, str]:
        if interface.payload.upper() == 'JSON':
            return service_response.json()

        return service_response.text

