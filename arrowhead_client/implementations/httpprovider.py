from functools import partial
from typing import Callable, Sequence, Any, Mapping, Optional
from flask import Flask, request
import flask
import ssl

from arrowhead_client.abc import BaseProvider, AccessPolicy
from arrowhead_client.service import Service
from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.security.utils import cert_cn
from arrowhead_client.configuration import config


class HttpProvider(BaseProvider):
    """ Class for provided_service provision """

    def __init__(
            self,
            system: ArrowheadSystem,
            keyfile: str = '',
            certfile:str = '', ) -> None:  # type: ignore
        app_name = str(config.get('app_name')) or __name__
        self.app = Flask(app_name)
        self.system = system
        self.keyfile = keyfile
        self.certfile = certfile
        if self.keyfile and self.certfile and config.get('certificate authority'):
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.load_verify_locations(str(config['certificate authority']))
            ssl_context.load_cert_chain(certfile, keyfile)
            self.ssl_context: Optional[ssl.SSLContext] = ssl_context
        else:
            self.ssl_context = None

    def add_provided_service(self,
                             service: Service,
                             method: str,
                             func: Callable,
                             access_policy: AccessPolicy,
                             *func_args: Sequence[Any],  # type: ignore
                             **func_kwargs: Mapping[Any, Any],  # type: ignore
                             ) -> None:
        """ Add provided_service to provider system"""
        # Register provided_service with Flask app
        # TODO: Add nested function which handles token authentication
        #func = partial(func, request, *func_args, **func_kwargs)
        def new_func(request, *func_args, **func_kwargs):
            auth = request.headers.get('authorization')
            consumer_cn = cert_cn(request.headers.environ.get('SSL_CLIENT_CERT'))
            is_authorized, auth_message = access_policy.is_authorized(
                    consumer_cn=consumer_cn,
                    provider=self.system,
                    provided_service=service,
                    token=auth,
            )

            if is_authorized:
                return func(request, *func_args, **func_kwargs)
            else:
                flask.abort(
                        403,
                        f'Not authorized to consume service'
                        f'{service.service_definition}@{self.system.authority}: '
                        f'{auth_message}.'
                )


        self.app.add_url_rule(rule=f'/{service.service_uri}',
                              endpoint=service.service_definition,
                              methods=[method],
                              view_func=partial(new_func, request, *func_args, **func_kwargs))

    def run_forever(self):
        self.app.run(host=self.system.address,
                     port=self.system.port,
                     ssl_context=self.ssl_context,
        )
