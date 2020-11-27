from typing import Mapping, Dict, Tuple, List
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service
from arrowhead_client.response import Response
from arrowhead_client.security import publickey_from_base64
from arrowhead_client import errors

system_keys = ('systemName', 'address', 'port', 'authenticationInfo')
service_keys = ('serviceDefinition', 'serviceUri', 'interfaces', 'secure')


def extract_system_data(system_data: Mapping) -> Dict:
    """ Extracts system data from core provided_service response """

    system_data = {key: system_data[key] for key in system_keys}

    return system_data


def extract_service_data(data: Mapping) -> Dict:
    """ Extracts provided_service data from core provided_service response """

    service_data = {key: data[key] for key in service_keys}

    service_data['serviceDefinition'] = service_data['serviceDefinition']['serviceDefinition']

    return service_data


def handle_service_query_response(service_query_response: Mapping) -> List[Tuple[Dict, Dict]]:
    """ Handles provided_service query responses and returns a lists of services and systems """

    service_query_data = service_query_response['serviceQueryData']

    service_and_system_list = [
        (extract_service_data(data), extract_system_data(data))
        for data in service_query_data
    ]

    return service_and_system_list


def handle_service_register_response(service_register_response: Mapping) -> None:
    """ Handles provided_service register responses """
    # TODO: Implement this
    raise NotImplementedError


def process_orchestration_response(service_orchestration_response: Response) \
        -> List[Tuple[Service, ArrowheadSystem, str]]:
    """ Turns orchestration response into list of services """
    if isinstance(service_orchestration_response.payload, dict):
        orchestration_response_list = service_orchestration_response.payload['response']
    else:
        raise ValueError('Response payload type must be \'JSON\'')

    def extract_orchestration_data(orchestration_response_entry):
        service_dto = orchestration_response_entry
        provider_dto = service_dto['provider']

        service_definition = service_dto['service']['serviceDefinition']
        service_uri = service_dto['serviceUri']
        interface = service_dto['interfaces'][0]['interfaceName']
        system_name = provider_dto['systemName']
        address = provider_dto['address']
        port = provider_dto['port']
        access_policy = orchestration_response_entry['secure']
        auth_token = service_dto['authorizationTokens']
        if auth_token:
            auth_token = auth_token.get(interface)


        service = Service(
                service_definition,
                service_uri,
                interface,
                access_policy,
        )

        system = ArrowheadSystem(
                system_name,
                address,
                port,
        )

        return service, system, auth_token


    extracted_data = [extract_orchestration_data(orchestration_entry)
                      for orchestration_entry in orchestration_response_list]

    if len(extracted_data) == 0:
        raise errors.NoAvailableServicesError()

    return extracted_data

def process_publickey(publickey_response: Response):
    encoded_key = publickey_response.payload

    return publickey_from_base64(encoded_key)

