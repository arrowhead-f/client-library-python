from functools import partial
from flask import Flask, request
import ssl

from arrowhead_client.abc import BaseProvider
from arrowhead_client.rules import RegistrationRule
from arrowhead_client import errors
from arrowhead_client.common import Constants


class HttpProvider(BaseProvider, protocol=Constants.PROTOCOL_HTTP):
    """ Class for provided_service provision """

    def __init__(self, cafile: str, app_name: str='') -> None:
        self.app_name = __name__ or app_name
        self.app = Flask(app_name)
        self.cafile = cafile

        @self.app.errorhandler(500)
        def internal_error(error):
            return {Constants.ERROR_MESSAGE: 'Internal issue'}

    def add_provided_service(self, rule: RegistrationRule) -> None:
        """ Add provided_service to provider system"""
        def func_with_access_policy(request):
            """Register provided_service with Flask app."""
            auth_string = request.headers.get('authorization')
            consumer_cert_str = request.headers.environ.get('SSL_CLIENT_CERT')
            try:
                is_authorized = rule.is_authorized(
                        consumer_cert_str=consumer_cert_str,
                        auth_str=auth_string,
                )
            except errors.AuthorizationError as e:
                is_authorized = False

            if not is_authorized:
                return {Constants.ERROR_MESSAGE:
                            f'Not authorized to consume service '
                            f'{rule.service_definition}@{rule.authority}/'
                            f'{rule.service_uri}'}, 403

            return rule.func(request)


        self.app.add_url_rule(
                rule=f'/{rule.service_uri}',
                endpoint=rule.service_definition,
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
