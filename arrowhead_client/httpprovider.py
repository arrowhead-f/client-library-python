from functools import partial
from typing import Callable, Sequence, Any, Mapping
from flask import Flask, request
import flask
import ssl

from arrowhead_client.abc import BaseProvider
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.security import AccessToken, cert_cn
from arrowhead_client.configuration import config

class HttpProvider(BaseProvider):
    """ Class for provided_service provision """

    def __init__(
            self,
            system: ArrowheadSystem,
            keyfile: str = '',
            certfile:str = '', ) -> None:  # type: ignore
        app_name = config.get('app_name') or __name__
        self.app = Flask(app_name)
        self.system = system
        self.keyfile = keyfile
        self.certfile = certfile
        if self.keyfile and self.certfile and config.get('certificate authority'):
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.load_verify_locations(config['certificate authority'])
            ssl_context.load_cert_chain(certfile, keyfile)
            self.ssl_context = ssl_context
        else:
            self.ssl_context = None

    def add_provided_service(self,
                             service: Service,
                             method: str,
                             func: Callable,
                             authorization_key = None,
                             *func_args: Sequence[Any],  # type: ignore
                             **func_kwargs: Mapping[Any, Any],  # type: ignore
                             ) -> None:
        """ Add provided_service to provider system"""
        # Register provided_service with Flask app
        # TODO: Add nested function which handles token authentication
        #func = partial(func, request, *func_args, **func_kwargs)
        def new_func(request, *func_args, **func_kwargs):
            if service.access_policy == 'TOKEN':
                auth = request.headers.get('authorization')
                token = AccessToken.from_string(auth, self.system._privatekey, authorization_key)
                consumer_cn = cert_cn(request.headers.environ.get('SSL_CLIENT_CERT'))
                service_definition = service.service_definition
                interface_definition = service.interface
                is_authorized = consumer_cn.startswith(token.consumer_id) and \
                                interface_definition == token.interface_id and \
                                service_definition == token.service_id
            elif service.access_policy == 'CERTIFICATE':
                is_authorized = bool(request.headers.environ.get('SSL_CLIENT_CERT'))
            elif service.access_policy == 'NOT_SECURE':
                is_authorized = True
            else:
                is_authorized = False

            if is_authorized:
                return func(request, *func_args, **func_kwargs)
            else:
                flask.abort(403, 'Not authorized')


        self.app.add_url_rule(rule=f'/{service.service_uri}',
                              endpoint=service.service_definition,
                              methods=[method],
                              view_func=partial(new_func, request, *func_args, **func_kwargs))

    def run_forever(self):
        self.app.run(host=self.system.address,
                     port=self.system.port,
                     ssl_context=self.ssl_context,
        )
