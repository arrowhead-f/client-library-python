from functools import partial
from flask import Flask, request
import flask
import ssl

from arrowhead_client.abc import BaseProvider
from arrowhead_client.rules import RegistrationRule
from arrowhead_client import errors


class HttpProvider(BaseProvider, protocol='HTTP'):
    """ Class for provided_service provision """

    def __init__(self, cafile: str, app_name='') -> None:
        self.app_name = __name__ or app_name
        self.app = Flask(app_name)
        self.cafile = cafile

    def add_provided_service(self, rule: RegistrationRule) -> None:
        """ Add provided_service to provider system"""
        # Register provided_service with Flask app
        def func_with_access_policy(request):
            auth_string = request.headers.get('authorization')
            consumer_cert_str = request.headers.environ.get('SSL_CLIENT_CERT')
            try:
                is_authorized = rule.access_policy.is_authorized(
                        consumer_cert_str=consumer_cert_str,
                        auth_header=auth_string,
                )
            except errors.AuthorizationError as e:
                is_authorized = False

            if is_authorized:
                return rule.func(request)
            else:
                flask.abort(
                        403,
                        f'Not authorized to consume service'
                        f'{rule.provided_service.service_definition}@'
                        f'{rule.provider_system.authority}: '
                        #f'{auth_message}.'
                )


        self.app.add_url_rule(
                rule=f'/{rule.provided_service.service_uri}',
                endpoint=rule.provided_service.service_definition,
                methods=[rule.method],
                # TODO: Create Request class similar to Response
                view_func=partial(func_with_access_policy, request)
        )

    def run_forever(
            self,
            address: str,
            port: int,
            keyfile: str,
            certfile: str,
            ):

        if keyfile and certfile and self.cafile:
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.load_verify_locations(self.cafile)
            ssl_context.load_cert_chain(certfile, keyfile)
        else:
            ssl_context = None

        self.app.run(host=address,
                     port=port,
                     ssl_context=ssl_context,
        )
