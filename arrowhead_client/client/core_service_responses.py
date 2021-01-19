from typing import Mapping, Tuple, List, Callable
from functools import wraps

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.response import Response
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.common import Constants
from arrowhead_client.security.utils import der_to_pem
from arrowhead_client import errors


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
            raise errors.NotAuthorizedError(core_service_response.read_json()[Constants.ERROR_MESSAGE])
        elif core_service_response.status_code == 500:
            raise errors.CoreServiceNotAvailableError(core_service_response.read_json()[Constants.ERROR_MESSAGE])

        return func(core_service_response, *args, **kwargs)

    return error_handling_wrapper


@core_service_error_handler
def process_service_query(query_response: Response) -> List[Tuple[Service, ArrowheadSystem]]:
    """ Handles provided_service query responses and returns a lists of services and systems """
    # TODO: Status 400 is general for all core systems and should be put in the handler.
    if query_response.status_code == 400:
        raise errors.CoreServiceInputError(query_response.read_json()[Constants.ERROR_MESSAGE])

    query_data = query_response.read_json()['serviceQueryData']

    service_and_system = [
        (
            _extract_service(query_result),
            ArrowheadSystem.from_dto(query_result['provider'])
        )
        for query_result in query_data
    ]

    return service_and_system


@core_service_error_handler
def process_service_register(service_register_response: Response) -> None:
    """ Handles service registration responses """
    if service_register_response.status_code == 400:
        raise errors.CoreServiceInputError(
                service_register_response.read_json()[Constants.ERROR_MESSAGE],
        )
    # TODO: Should return a string representing the successfully registered service for logging?


@core_service_error_handler
def process_service_unregister(service_unregister_response: Response) -> None:
    """ Handles service unregistration responses """
    if service_unregister_response.status_code == 400:
        raise errors.CoreServiceInputError(
                service_unregister_response.read_json()[Constants.ERROR_MESSAGE]
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
        raise errors.OrchestrationError(orchestration_response.read_json()[Constants.ERROR_MESSAGE])

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

    service = _extract_service(service_dto)

    system = ArrowheadSystem.from_dto(provider_dto)

    interface = service_dto['interfaces'][0]['interfaceName']
    auth_tokens = service_dto['authorizationTokens']
    auth_token = auth_tokens.get(interface, '') if auth_tokens else ''

    return OrchestrationRule(service, system, method, auth_token)


def _extract_service(query_data: Mapping) -> Service:
    """ Extracts provided_service data from test_core provided_service response """
    if 'serviceDefinition' in query_data:
        service_definition_base = 'serviceDefinition'
    elif 'service' in query_data:
        service_definition_base = 'service'
    else:
        raise ValueError

    service = Service(
            query_data[service_definition_base]['serviceDefinition'],
            query_data['serviceUri'],
            ServiceInterface.from_str(query_data['interfaces'][0]['interfaceName']),
            query_data['secure'],
            query_data['metadata'],
            query_data['version'],
    )

    return service
