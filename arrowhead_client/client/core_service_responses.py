from typing import Mapping, Dict, Tuple, List
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service

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


def handle_service_query_response(service_query_response: Mapping) -> List[Tuple[Dict, Dict]]:
    """ Handles service query responses and returns a lists of services and systems """

    service_query_data = service_query_response['serviceQueryData']

    service_and_system_list = [
        (extract_service_data(data), extract_system_data(data))
        for data in service_query_data
    ]

    return service_and_system_list


def handle_service_register_response(service_register_response: Mapping) -> None:
    """ Handles service register responses """
    # TODO: Implement this
    raise NotImplementedError


def handle_orchestration_response(service_orchestration_response: Mapping) \
        -> List[Tuple[Service, ArrowheadSystem]]:
    """ Turns orchestration response into list of services """
    orchestration_response_list = service_orchestration_response['response']

    extracted_data = []
    for orchestration_response in orchestration_response_list:
        service_dto = orchestration_response
        provider_dto = service_dto['provider']

        service_definition = service_dto['service']['serviceDefinition']
        service_uri = service_dto['serviceUri']
        interface = service_dto['interfaces'][0]['interfaceName']
        system_name = provider_dto['systemName']
        address = provider_dto['address']
        port = provider_dto['port']

        service = Service(
                service_definition,
                service_uri,
                interface,
        )

        system = ArrowheadSystem(
                system_name,
                address,
                port,
                ''
        )

        extracted_data.append((service, system))

    return extracted_data
