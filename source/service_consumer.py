import requests
from arrowhead_system import ArrowheadSystem
from dataclasses import asdict
from pprint import pprint

class ServiceConsumer():
    def __init__(self,
            name = 'Default',
            address = 'localhost',
            port = '8080',
            authentication_info = '',
            consumer_system = None,
            requested_service = {},
            orchestration_flags = {},
            service_registry = None,
            orchestrator = None):
        if consumer_system:
        # Use the given consumer system
            self.system = consumer_system
        else:
        # or create a new from the data given
            self.system = ArrowheadSystem(name, 
                    address, 
                    port, 
                    authentication_info)
        self.req_service = requested_service
        self.orch_flags = orchestration_flags
        self.service_registry = service_registry
        assert self.service_registry
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

    def service_query_form(self,
            service_definition = 'default',
            interfaces = [],
            service_metadata = {},
            ping_providers = False,
            metadata_search = False):
        """ Note: This function should be in utils """
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

    def find_core_systems(self):
        #  Create forms for the orchestrator and authorization system
        #  This is a hack as I am querying the service registry for systems, should be
        # changed to use the system registry once it is up
        #  Only insecure is supported for now
        orch_form = self.service_query_form(service_definition = 'InsecureOrchestrationService')
        auth_form = self.service_query_form(service_definition = 'InsecureAuthorizationControl')
        # Query the service registry for the orchestrator and authorization systems,
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

    def service_request_form(self, 
            requested_service = {},
            orchestration_flags = {}):
        """ This function should be in utils """
        if not orchestration_flags:
            orchestration_flags = {
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
        service_request_form = {
                'requesterSystem': asdict(self.system),
                'requestedService': requested_service,
                'orchestrationFlags': orchestration_flags,
                'preferredProviders': [],
                'requestedQoS': {},
                'commands': {}
                }
        return service_request_form

    def consume(self):
        pass

    def service_query(self, service_query_form=None):
        if not self.service_registry:
            print("No service registry")
            assert self.service_registry
        if not service_query_form:
            print('Please choose a service to query')
            assert service_query_form
        sr_url = f'http://{self.service_registry.address}:{self.service_registry.port}/serviceregistry/query'
        response = requests.put(sr_url, json=service_query_form)
        print(response.status_code)
        assert response.ok
        return response.json()
    
    def service_request(self, service_name = ''):
        service_request_form = self.service_request_form(
                requested_service = {'serviceDefinition': service_name,
                    'interfaces': [],
                    'serviceMetadata': {}})
        pprint(service_request_form)
        orch_url = f'http://{self.orchestrator.address}:{self.orchestrator.port}/orchestrator/orchestration'
        response = requests.post(orch_url, json=service_request_form)
        pprint(response.json())

if __name__ == '__main__':
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8442')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')
    consumer = ServiceConsumer(service_registry=service_registry, consumer_system=test_consumer)
    a = consumer.system_name
    print(a)
    default_query_form = consumer.service_query_form('default')
    pprint(default_query_form)
    pprint(consumer.service_query(default_query_form)['serviceQueryData'])
    pprint(consumer.orchestrator)
    pprint(consumer.authorization)
    consumer.service_request('default')
