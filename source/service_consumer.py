import requests
from arrowhead_system import ArrowheadSystem
from dataclasses import asdict
from pprint import pprint
from utils import move_to_utils
import json

class ServiceConsumer():
    def __init__(self,
            name = 'Default',
            address = 'localhost',
            port = '8080',
            authentication_info = '',
            consumer_system = None,
            requested_service = None,
            # Why do I want to encode the requested service here?
            orchestration_flags = None,
            service_registry = None,
            config_file = ''):
        if consumer_system:
        # Use the given consumer system
            self.system = consumer_system
        else:
        # or create a new from the data given
            self.system = ArrowheadSystem(name, 
                    address, 
                    port, 
                    authentication_info)
        if not requested_service:
            self.req_service = []
        else:
            self.req_service = requested_service

        if not orchestration_flags:
            self.orchestration_flags = {
                    'onlyPreferred': False,
                    'overrideStore': True,
                    'externalServiceRequest': False,
                    'enableInterCloud': False,
                    'enableQoS': False,
                    'matchmaking': False,
                    'metadataSearch': False,
                    'triggerInterCloud': False,
                    'pingProviders': False
                    }
        else:
            self.orchestration_flags = orchestration_flags
        assert service_registry
        self.service_registry = service_registry

        self.orchestrator, self.authorization = self.find_core_systems()

    @property
    def system_name(self):
        return self.system.systemName

    @property
    def address(self):
        return self.system.address

    @property
    def port(self):
        return self.system.port

    @move_to_utils
    def service_query_form(self,
            service_definition = 'default',
            interfaces = None,
            service_metadata = None,
            ping_providers = False,
            metadata_search = False):
        """ Note: This function should be in utils """
        if not interfaces:
            interfaces = []
        if not service_metadata:
            service_metadata = {}

        query_form = {
            'service': {
                'serviceDefinition': service_definition,
                'interfaces': interfaces,
                'serviceMetadata': service_metadata
            },
            'pingProviders': ping_providers,
            'metadataSearch': metadata_search,
            'version': None
        }
        return query_form

    def find_core_systems(self, insecure=True):
        if insecure:
            # Only the insecure core systems are supported for now
            orch_definition = 'InsecureOrchestrationService'
            auth_definition = 'InsecureAuthorizationControl'
        else:
            # Even though the definitions are here, the secure systems are not supported
            orch_definition = 'SecureOrchestrationService'
            auth_definition = 'SecureAuthorizationService'
        # Query the service registry to get the location of the core services
        orch_form = self.service_query_form(service_definition=orch_definition)
        auth_form = self.service_query_form(service_definition=auth_definition)
        # keeping only the provider part (should be easier with system registry)
        
        orch_result = self.service_query(orch_form)['serviceQueryData'][0]['provider']
        auth_result = self.service_query(auth_form)['serviceQueryData'][0]['provider']
        orchestrator = ArrowheadSystem(systemName=orch_result['systemName'],
                address=orch_result['address'],
                port=orch_result['port'])
        authorization_system = ArrowheadSystem(systemName=auth_result['systemName'],
                address=auth_result['address'],
                port=auth_result['port'])

        return orchestrator, authorization_system

    @move_to_utils
    def service_request_form(self, 
            requested_service = None,
            orchestration_flags = None):
        """ This function should be in utils """
        orchestration_flags = self.orchestration_flags

        service_request_form = {
                'requesterSystem': asdict(self.system),
                'requestedService': requested_service,
                'orchestrationFlags': orchestration_flags,
                'preferredProviders': [],
                'requestedQoS': {},
                'commands': {}
                }
        return service_request_form

    def service_query(self, service_query_form=None):
        if not self.service_registry:
            print("No service registry")
            assert self.service_registry
        if not service_query_form:
            print('Please choose a service to query')
            assert service_query_form
        sr_url = f'http://{self.service_registry.address}:{self.service_registry.port}/serviceregistry/query'
        response = requests.put(sr_url, json=service_query_form)
        #print(response.status_code)
        assert response.ok
        return response.json()

    def service_request(self, service_name = ''):
        # Create service request form
        service_request_form = self.service_request_form(
                requested_service = {'serviceDefinition': service_name,
                    'interfaces': [],
                    'serviceMetadata': {}})
        # Create orchestrator url
        orch_url = f'http://{self.orchestrator.address}:{self.orchestrator.port}/orchestrator/orchestration'
        # Query the ochestration service
        response = requests.post(orch_url, json=service_request_form)
        # extract information from orchestration response
        provider_system = response.json()['response'][0]['provider']
        provider_service_uri = response.json()['response'][0]['serviceURI']
        # Create uri for requested service
        service_uri = f'http://{provider_system["address"]}:{provider_system["port"]}{provider_service_uri}'
        # Return uri for requested service
        return service_uri

    def consume(self, service_name='', service_method=''):
        provider_uri = self.service_request(service_name)
        return requests.get(f'{provider_uri}/{service_method}')

if __name__ == '__main__':
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8442')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')
    consumer = ServiceConsumer(service_registry=service_registry, consumer_system=test_consumer)
    a = consumer.system_name
    #print(a)
    default_query_form = consumer.service_query_form('default')
    #print(json.dumps(default_query_form))
    #pprint(consumer.service_query(default_query_form)['serviceQueryData'])
    #pprint(consumer.orchestrator)
    #pprint(consumer.authorization)
    #consumer_uri = consumer.service_request('default')
    #print(f'{consumer_uri}/test')
    #r = requests.get(f'{consumer_uri}/test')
    #print(r.text)
    service_consumption = consumer.consume('default', 'test')
    print(service_consumption.text)
