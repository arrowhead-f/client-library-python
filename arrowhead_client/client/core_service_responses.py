from typing import Mapping, Tuple, List, Callable
from functools import wraps

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service
from arrowhead_client.response import Response
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.security.utils import der_to_pem
from arrowhead_client import errors

system_keys = {'systemName', 'address', 'port', 'authenticationInfo'}
service_keys = {'serviceDefinition', 'serviceUri', 'interfaces', 'secure'}


def core_service_error_handler(func) -> Callable:
    """
    Decorator that raises the appropriate exception with a
    standard message when the core service returns an error.

    Raises:
        # TODO: errors.CoreServiceInputError: If return status is 400.
        # or not, this might be core-service specific whether that is good or not
        errors.NotAuthorizedError: If return status is 401.
        errors.CoreServiceNotAvailableError: If return status is 500.
    """

    @wraps(func)
    def error_handling_wrapper(core_service_response: Response, *args, **kwargs):
        if core_service_response.status_code == 401:
            raise errors.NotAuthorizedError(core_service_response.read_json()['errorMessage'])
        elif core_service_response.status_code == 500:
            raise errors.CoreServiceNotAvailableError(core_service_response.read_json()['errorMessage'])

        return func(core_service_response, *args, **kwargs)

    return error_handling_wrapper


@core_service_error_handler
def process_service_query(query_response: Response) -> List[Tuple[Service, ArrowheadSystem]]:
    """ Handles provided_service query responses and returns a lists of services and systems """
    # TODO: Status 400 is general for all core systems and should be put in the handler.
    if query_response.status_code == 400:
        raise errors.CoreServiceInputError(query_response.read_json()['errorMessage'])

    query_data = query_response.read_json()['serviceQueryData']

    service_and_system = [
        (
            _extract_service(query_result),
            _extract_system(query_result)
        )
        for query_result in query_data
    ]

    return service_and_system


@core_service_error_handler
def process_service_register(service_register_response: Response) -> None:
    """ Handles service registration responses """
    if service_register_response.status_code == 400:
        raise errors.CoreServiceInputError(
                service_register_response.read_json()['errorMessage'],
        )
    # TODO: Should return a string representing the successfully registered service for logging?


@core_service_error_handler
def process_service_unregister(service_unregister_response: Response) -> None:
    """ Handles service unregistration responses """
    if service_unregister_response.status_code == 400:
        raise errors.CoreServiceInputError(
                service_unregister_response.read_json()['errorMessage']
        )
    # TODO: Should return a string representing the successfully unregistered service for logging?


@core_service_error_handler
def process_orchestration(orchestration_response: Response, method='') \
        -> List[OrchestrationRule]:
    """
    Turns orchestration response into list of services.

    Args:
        orchestration_response: Response object from orchestration.
        method: Method
    Returns:
        List of OrchestrationRules found in the orchestration response.
    """
    if orchestration_response.status_code == 400:
        raise errors.OrchestrationError(orchestration_response.read_json()['errorMessage'])

    orchestration_results = orchestration_response.read_json().get('response', [])

    extracted_rules = [
        _extract_orchestration_rules(orchestration_result, method)
        for orchestration_result in orchestration_results
    ]

    return extracted_rules


@core_service_error_handler
def process_publickey(publickey_response: Response) -> str:
    encoded_key = publickey_response.payload.decode()

    return der_to_pem(encoded_key)


def _extract_orchestration_rules(orchestration_result, method) -> OrchestrationRule:
    """
    Helper function to extract orchestration rules from an orchestration result.

    Args:
        orchestration_result: An orchestration result.
    Returns:
        Orchestration rule extracted from the orchestration result.
    """
    service_dto = orchestration_result
    provider_dto = service_dto['provider']

    service_definition = service_dto['service']['serviceDefinition']
    service_uri = service_dto['serviceUri']
    interface = service_dto['interfaces'][0]['interfaceName']
    system_name = provider_dto['systemName']
    address = provider_dto['address']
    port = provider_dto['port']
    access_policy = orchestration_result['secure']
    auth_tokens = service_dto['authorizationTokens']
    auth_token = auth_tokens.get(interface, '') if auth_tokens else ''

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

    return OrchestrationRule(service, system, method, auth_token)


def _extract_system(query_data: Mapping) -> ArrowheadSystem:
    """ Extracts system data from test_core provided_service response """

    system = ArrowheadSystem.from_dto(query_data['provider'])

    return system


def _extract_service(query_data: Mapping) -> Service:
    """ Extracts provided_service data from test_core provided_service response """

    service = Service(
            query_data['serviceDefinition']['serviceDefinition'],
            query_data['serviceUri'],
            query_data['interfaces'][0]['interfaceName'],
            query_data['secure'],
            query_data['metadata'],
            query_data['version'],
    )

    return service
