from functools import partial
from typing import Optional, Callable, Dict, Tuple, Sequence, Any, Mapping
from flask import Flask, request
from arrowhead_client.service import Service


class Provider():
    """ Class for service provision """

    def __init__(self) -> None:
        self.app = Flask(__name__) # Necessary
        self.provided_services: Dict[str, Tuple[Service, Callable]] = {} # Necessary

    def add_provided_service(self,
                             provided_service: Service,
                             http_method: str = '',
                             view_func: Optional[Callable] = None,
                             *func_args: Sequence[Any], # type: ignore
                             ** func_kwargs: Mapping[Any, Any],  # type: ignore
                             ) -> None:
        """ Add service to provider system"""
        #TODO: This method does two thing at once. It adds a service from parameters,
        # and it adds an already created service. These functionalities should be
        # separated. Or maybe not?

        if provided_service.service_definition not in self.provided_services.keys() and \
            callable(view_func):
            # Register service with Flask app
            self.provided_services[provided_service.service_definition] = (provided_service, view_func)
            view_func = partial(view_func, request, *func_args, **func_kwargs)
            self.app.add_url_rule(rule=f'/{provided_service.service_uri}',
                                  endpoint=provided_service.service_definition,
                                  methods=[http_method],
                                  view_func=view_func)
        else:
            # TODO: Add log message when service is trying to be overwritten
            pass

    def provided_service(self,
                         service_definition: str,
                         service_uri: str,
                         interface: str,
                         method: str,
                         *func_args,
                         **func_kwargs,) -> Callable:
        """ Decorator to add provided services """

        service = Service(
                service_definition,
                service_uri,
                interface,
        )

        def wrapped_func(func):
            self.add_provided_service(
                    service,
                    http_method=method,
                    view_func=func,
                    *func_args,
                    **func_kwargs,)
            return partial(func, *func_args, **func_kwargs)
        return wrapped_func

