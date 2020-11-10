from functools import partial
from typing import Callable, Sequence, Any, Mapping
from flask import Flask, request

from arrowhead_client.abc import BaseProvider


class HttpProvider(BaseProvider):
    """ Class for service provision """

    def __init__(
            self,
            wsgi_server: Any, ) -> None:  # type: ignore
        self.app = Flask(__name__)
        self.wsgi_server = wsgi_server
        self.wsgi_server.application = self.app

    def add_provided_service(self,
                             service_definition: str,
                             service_uri: str,
                             method: str,
                             func: Callable,
                             *func_args: Sequence[Any],  # type: ignore
                             **func_kwargs: Mapping[Any, Any],  # type: ignore
                             ) -> None:
        """ Add service to provider system"""

        # Register service with Flask app
        func = partial(func, request, *func_args, **func_kwargs)
        self.app.add_url_rule(rule=f'/{service_uri}',
                              endpoint=service_definition,
                              methods=[method],
                              view_func=func)

    def run_forever(self):
        self.wsgi_server.serve_forever()
