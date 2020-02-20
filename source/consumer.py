from pprint import pprint
from dataclasses import dataclass
from functools import partial
import requests
from source.service import ConsumedService, ProviderSystem

class BaseConsumer():
    def __init__(self):
        ''' BaseConsumer '''
        self.rule_dictionary = {}

    def add_orchestration_rule(self, rule, http_method, service_definition=None):
        ''' Add orchestration rule into rule dictionary '''

        # Currently extracts only the first orchestration response
        self.rule_dictionary[rule] = {'method': http_method, 
                                      'service': self.query_orchestration(service_definition)[0]}

    def query_orchestration(self, service_definition=None):
        ''' Query orchestration for a particular service '''
        if not service_definition:
            requested_service = None
        else:
            requested_service = {
                    "serviceDefinitionRequirement": service_definition,
                    "interfaceRequirements": None,
                    "securityRequirements": None,
                    "metadataRequirements": None,
                    "versionRequirement": None,
                    "maxVersionRequirement": None,
                    "minVersionRequirement": None
                    }

            orchestration_form = {
                    "commands": None,
                    "orchestrationFlags": {
                        "overrideStore": True if service_definition else False
                        },
                    "preferredProviders": None,
                    "requestedService": requested_service,
                    "requesterCloud": None,
                    "requesterSystem": self.system_json
                    }

            orchestration_response = requests.post(f'https://{self.orch_url}/orchestration',
                    cert=(self.certfile, self.keyfile),
                    verify=False,
                    json=orchestration_form)

            extracted_services = [ConsumedService.from_orch_response(orch_r)
                    for orch_r in orchestration_response.json()['response']]

            return extracted_services

    def consume(self, rule, payload=None, json=None):
        ''' Consumes service under rule '''
        if not rule in self.rule_dictionary:
            raise ValueError('Consumed rule is not registered')

        method, service = self.rule_dictionary[rule].values()
        if method.upper() == 'GET':
            response = requests.get(service.url,
                    cert=(self.certfile, self.keyfile),
                    verify=False)
        if method.upper() == 'POST':
            response = requests.post(service.url, data=payload, json=json,
                    cert=(self.certfile, self.keyfile),
                    verify=False)
        if method.upper() == 'PUT':
            response = requests.put(service.url, data=payload, json=json,
                    cert=(self.certfile, self.keyfile),
                    verify=False)
        if method.upper() == 'DELETE':
            response = requests.delete(service.url,
                    cert=(self.certfile, self.keyfile),
                    verify=False)

        return response
