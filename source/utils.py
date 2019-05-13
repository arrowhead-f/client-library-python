from dataclasses import dataclass, field, asdict
from arrowhead_system import ArrowheadSystem
import requests
from functools import wraps

def move_to_utils(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(f"The object {f.__name__} should be moved to utils")
        return f(*args, **kwargs)
    return wrapper

def service_query_form(
        service_definition = 'default',
        interfaces = None,
        service_metadata = None,
        ping_providers = False,
        metadata_search = False):
    """ Creates a service request form to be sent to the service registry """
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

def service_query(service_registry=None, service_query_form=None):
    """ Queries the given service registry with the given service request form """
    if not service_registry:
        print("No service registry")
        assert service_registry
    if not service_query_form:
        print('Please choose a service to query')
        assert service_query_form
    sr_url = f'http://{service_registry.address}:{service_registry.port}/serviceregistry/query'
    response = requests.put(sr_url, json=service_query_form)
    #print(response.status_code)
    assert response.ok
    return response.json()

def find_core_systems(service_registry=None, insecure=True):
    """ Function to find the core systems of the local cloud """
    """ To implement:
            - Find the rest of the core systems
            - *Enable selection of core systems
    """
    if insecure:
        # Only the insecure core systems are supported for now
        orch_definition = 'InsecureOrchestrationService'
        auth_definition = 'InsecureAuthorizationControl'
    else:
        # Even though the definitions are here, the secure systems are not supported
        orch_definition = 'SecureOrchestrationService'
        auth_definition = 'SecureAuthorizationService'
    # Query the service registry to get the location of the core services
    orch_form = service_query_form(service_definition=orch_definition)
    auth_form = service_query_form(service_definition=auth_definition)
    # keeping only the provider part (should be easier with system registry)
    orch_result = service_query(service_registry, orch_form)['serviceQueryData'][0]['provider']
    auth_result = service_query(service_registry, auth_form)['serviceQueryData'][0]['provider']
    orchestrator = ArrowheadSystem(systemName=orch_result['systemName'],
            address=orch_result['address'],
            port=orch_result['port'])
    authorization_system = ArrowheadSystem(systemName=auth_result['systemName'],
            address=auth_result['address'],
            port=auth_result['port'])

    return orchestrator, authorization_system
