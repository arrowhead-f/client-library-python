import requests
from arrowhead_system import ArrowheadSystem
from dataclasses import asdict
from pprint import pprint
#from utils import move_to_utils
import utils
import json

class ServiceConsumer():
    def __init__(self,
            name = 'Default',
            address = 'localhost',
            port = '8080',
            authentication_info = '',
            system = None,
            requested_service = None,
            # Why do I want to encode the requested service here?
            # Maybe so I could run .consume() without arguments?
            orchestration_flags = None,
            service_registry = None,
            config_file = ''):
        if system:
            # Use the given consumer system
            self.system = system
        else:
            # or create a new from the data given
            self.system = ArrowheadSystem(name, 
                    address, 
                    port, 
                    authentication_info)
        if requested_service:
            # When I wrote this initially I thought it might be a good idea to store the requested services so I don't have to query the orchestrator every single time.
            # I still like the idea but I'm not sure how I should implement it right now.
            self.req_service = requested_service
        else:
            self.req_service = []

        if orchestration_flags:
            self.orchestration_flags = orchestration_flags
        else:
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
            assert service_registry
        self.service_registry = service_registry

        self.orchestrator, self.authorization = utils.find_core_systems(self.service_registry)

    @property
    def system_name(self):
        return self.system.systemName

    @property
    def address(self):
        return self.system.address

    @property
    def port(self):
        return self.system.port

    def service_request_form(self, 
            requested_service = None,
            orchestration_flags = None):
        """ This function should be in utils """
        """ 
        This method creates a service request form in the form of a dictionary.
        """

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

    def service_request(self, service_name = ''):
        """
        Query the orchestrator for a service

        To be implemented:
         - Checks to see what went wrong
        """
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
        """
            Consume method service_method of service service_name
        """
        provider_uri = self.service_request(service_name)
        # Currently, the line above means that every time the consumer tries to consume a service it queries the orchestrator to get the uri. It is good enough for now, but some sort of cache needs to be implemented to reduce SoS overhead.
        # Like as long as HTTP 200 is returned nothing new needs to be done but if 404 is returned it should requery the orchestrator to renew the information.
        # The cache could be implemented as a dictionary.
        return requests.get(f'{provider_uri}/{service_method}')

if __name__ == '__main__':
    service_registry = ArrowheadSystem('Service registry', '127.0.0.1', '8442')
    test_consumer = ArrowheadSystem('Test_Consumer', '127.0.0.1', '6006')
    consumer = ServiceConsumer(service_registry=service_registry, system=test_consumer)
    a = consumer.system_name
    #print(a)
    #default_query_form = consumer.service_query_form('default')
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
