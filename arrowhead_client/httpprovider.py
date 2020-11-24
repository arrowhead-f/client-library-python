from functools import partial
from typing import Callable, Sequence, Any, Mapping
from flask import Flask, request

from arrowhead_client.abc import BaseProvider
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.security import AccessToken

class HttpProvider(BaseProvider):
    """ Class for service provision """

    def __init__(
            self,
            wsgi_server: Any, ) -> None:  # type: ignore
        self.app = Flask(__name__)
        self.wsgi_server = wsgi_server
        self.wsgi_server.application = self.app

    def add_provided_service(self,
                             service: Service,
                             provider: ArrowheadSystem,
                             method: str,
                             func: Callable,
                             authorization_key = None,
                             *func_args: Sequence[Any],  # type: ignore
                             **func_kwargs: Mapping[Any, Any],  # type: ignore
                             ) -> None:
        """ Add service to provider system"""

        # Register service with Flask app
        # TODO: Add nested function which handles token authentication
        #func = partial(func, request, *func_args, **func_kwargs)
        def new_func(request, *func_args, **func_kwargs):
            bearer, token = request.headers['authorization'].split()
            token = AccessToken.from_string(token, provider._privatekey, authorization_key)
            return func(request, *func_args, **func_kwargs)


        self.app.add_url_rule(rule=f'/{service.service_uri}',
                              endpoint=service.service_definition,
                              methods=[method],
                              view_func=partial(new_func, request, *func_args, **func_kwargs))

    def run_forever(self):
        self.wsgi_server.serve_forever()
