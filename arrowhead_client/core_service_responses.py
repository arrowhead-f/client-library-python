#!/usr/bin/env python

from typing import Mapping, Dict, Sequence, List, Optional
from collections import namedtuple
from .service import ConsumedHttpService

ServiceAndSystem = namedtuple('ServiceAndSystem', ['service', 'system'])

system_keys = ('systemName', 'address', 'port', 'authenticationInfo')
service_keys = ('serviceDefinition', 'serviceUri', 'interfaces', 'secure')


def extract_system_data(system_data: Mapping) -> Dict:
    """ Extracts system data from core service response """

    system_data = {key: system_data[key] for key in system_keys}

    return system_data


def extract_service_data(data: Mapping) -> Dict:
    """ Extracts service data from core service response """

    service_data = {key: data[key] for key in service_keys}

    service_data['serviceDefinition'] = service_data['serviceDefinition']['serviceDefinition']

    return service_data


def handle_service_query_response(service_query_response: Mapping) -> List[ServiceAndSystem]:
    """ Handles service query responses and returns a lists of services and systems """

    service_query_data = service_query_response['serviceQueryData']

    services_and_systems = []

    for data in service_query_data:
        service = extract_service_data(data)
        system = extract_system_data(data['provider'])

        services_and_systems.append(ServiceAndSystem(service, system))

    return services_and_systems


def handle_service_register_response(service_register_response: Mapping) -> NotImplemented:
    """ Handles service register responses """
    # TODO: Implement this


def handle_orchestration_response(service_orchestration_response: Mapping) \
        -> Optional[ConsumedHttpService]:
    """ Turns orchestration response into list of services """
    service_list_dto = service_orchestration_response['response']

    service_dto = service_list_dto[0]
    provider_dto = service_dto['provider']

    service_definition = service_dto['service']['serviceDefinition']
    service_uri = service_dto['serviceUri']
    interface = service_dto['interfaces'][0]['interfaceName']
    address = provider_dto['address']
    port = provider_dto['port']

    service = ConsumedHttpService(
            service_definition,
            service_uri,
            interface,
            address,
            port,
            None,
    )
    # TODO: Return list of services instead of just the first one

    return service
