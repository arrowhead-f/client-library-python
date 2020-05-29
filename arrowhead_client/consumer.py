from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Callable, Dict, Union

import requests as backend
from arrowhead_client.core_service_forms import OrchestrationForm
from arrowhead_client.core_service_responses import handle_orchestration_response
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

    @property
    def cert(self) -> Tuple[str, str]:
        return self.certfile, self.keyfile

    def add_consumed_service(self,
                             service_definition: str,
                             consumer_system_dto: Dict,
                             http_method: str) -> None:
        """ Add orchestration rule for service definition """

        orchestration_form = OrchestrationForm(consumer_system_dto, service_definition)

        orchestration_response = self.consume_service('orchestration-service',
                                                      json=orchestration_form.dto,
                                                      )
        #TODO: Handle orchestrator error codes

        orchestration_payload = orchestration_response.json() # This might change with backend

        orchestrated_service, system = handle_orchestration_response(orchestration_payload)[0]

        #TODO: Handle response with more than 1 service
        # Perhaps a list of consumed services for each service definition should be stored
        self._register_consumed_service(orchestrated_service, system, http_method)

    def consume_service(self, service_definition: str, **kwargs) -> backend.Response:
        """ Consume registered service """
        # TODO: Add error handling for the case where the service is not
        # registered in _consumed_services

        uri, http_method = self._service_uri(service_definition)

        service_response = backend.request(http_method, uri, cert=self.cert, verify=False, **kwargs)

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

    def _register_consumed_service(self,
                                   service: Service,
                                   system: System,
                                   http_method: str) -> None:
        """ Register consumed services with the consumer """

        self._consumed_services[service.service_definition] = (service, system, http_method)
