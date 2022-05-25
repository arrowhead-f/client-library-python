from typing import Tuple, List, Callable
from functools import wraps

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service, ServiceInterface
from arrowhead_client.response import Response
from arrowhead_client.rules import OrchestrationRule
from arrowhead_client.security.utils import der_to_pem
from arrowhead_client import errors
import arrowhead_client.client.core_service_forms.client as client_forms
from arrowhead_client import constants


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
            raise errors.NotAuthorizedError(core_service_response.read_json()[constants.Misc.ERROR_MESSAGE])
        elif core_service_response.status_code == 500:
            raise errors.CoreServiceNotAvailableError(core_service_response.read_json()[constants.Misc.ERROR_MESSAGE])

        return func(core_service_response, *args, **kwargs)

    return error_handling_wrapper


@core_service_error_handler
def process_service_query(query_response: Response) -> List[Tuple[Service, ArrowheadSystem]]:
    """ Handles provided_service query responses and returns a lists of services and systems """
    # TODO: Status 400 is general for all core systems and should be put in the handler.
    if query_response.status_code == 400:
        raise errors.CoreServiceInputError(query_response.read_json()[constants.Misc.ERROR_MESSAGE])

    query_response_ = client_forms.ServiceQueryResponse(**query_response.read_json())

    service_and_system = [
        (
            Service(
                    service_definition=query_result.service_definition.service_definition,
                    service_uri=query_result.service_uri,
                    interface=ServiceInterface.from_str(query_result.interfaces[0].interface_name),
                    access_policy='',
                    metadata=query_result.metadata,
                    version=query_result.version,
            ),
            ArrowheadSystem(**query_result.provider.dict())
        )
        for query_result in query_response_.service_query_data
    ]

    return service_and_system


@core_service_error_handler
def process_service_register(service_register_response: Response):
    """ Handles service registration responses """
    if service_register_response.status_code == 400:
        raise errors.CoreServiceInputError(
                service_register_response.read_json()[constants.Misc.ERROR_MESSAGE],
        )
    # TODO: Should return a string representing the successfully registered service for logging?
    return client_forms.ServiceRegistryEntry(**service_register_response.read_json())


@core_service_error_handler
def process_service_unregister(service_unregister_response: Response) -> None:
    """ Handles service unregistration responses """
    if service_unregister_response.status_code == 400:
        raise errors.CoreServiceInputError(
                service_unregister_response.read_json()[constants.Misc.ERROR_MESSAGE]
        )
    # TODO: Should return a string representing the successfully unregistered service for logging?


@core_service_error_handler
def process_orchestration(orchestration_response: Response, method='') -> List[OrchestrationRule]:
    """
    Turns orchestration response into list of services.

    Args:
        orchestration_response: Response object from orchestration.
        method: Method
    Returns:
        List of OrchestrationRules found in the orchestration response.
    """
    if orchestration_response.status_code == 400:
        raise errors.OrchestrationError(orchestration_response.read_json()[constants.Misc.ERROR_MESSAGE])

    orchestration_results = client_forms.OrchestrationResponseList(
            **orchestration_response.read_json()
    ).response

    extracted_rules = [
        _extract_orchestration_rules(orchestration_result, method)
        for orchestration_result in orchestration_results
    ]

    return extracted_rules


@core_service_error_handler
def process_publickey(publickey_response: Response) -> str:
    encoded_key = publickey_response.payload.decode()

    return der_to_pem(encoded_key)


def _extract_orchestration_rules(
        orchestration_result: client_forms.OrchestrationResponse,
        method,
) -> OrchestrationRule:
    """
    Helper function to extract orchestration rules from an orchestration result.

    Args:
        orchestration_result: An orchestration result.
    Returns:
        Orchestration rule extracted from the orchestration result.
    """
    service_dto = orchestration_result
    provider_dto = service_dto.provider

    service = _extract_service(service_dto)

    system = ArrowheadSystem(**provider_dto.dict())

    interface = service_dto.interfaces[0].interface_name
    auth_tokens = service_dto.authorization_tokens
    auth_token = auth_tokens.get(interface, '') if auth_tokens else ''

    return OrchestrationRule(service, system, method, auth_token)


def _extract_service(query_data: client_forms.OrchestrationResponse) -> Service:
    """ Extracts provided_service data from test_core provided_service response """
    # TODO: this code guarded against different versions of OrchestrationResponse, not sure why
    '''
    if 'serviceDefinition' in query_data.dict():
        service_definition_base = 'serviceDefinition'
    elif 'service' in query_data.dict():
        service_definition_base = 'service'
    else:
        raise ValueError
    '''

    service = Service(
            query_data.service.service_definition,
            query_data.service_uri,
            ServiceInterface.from_str(query_data.interfaces[0].interface_name),
            query_data.secure,
            query_data.metadata,
            query_data.version,
    )

    return service
