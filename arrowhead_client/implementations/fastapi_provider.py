from typing import Mapping, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from arrowhead_client.abc import BaseProvider
from arrowhead_client.common import Constants
from arrowhead_client.rules import RegistrationRule
from arrowhead_client import errors

class ArrowheadAccessPolicyMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
            policy_map: Mapping[str, RegistrationRule],
    ):
        super().__init__(app)
        self.policy_map = policy_map

    async def dispatch(self, request: Request, call_next):
        path = request.scope['path'].strip('/')
        # TODO: Replace these with actual request values when uvicorn implements client-certs or when you try running a reverse proxy
        consumer_cert = 'consumer_cert'
        auth_str = 'auth_str'

        if not self.policy_map[path].is_authorized(consumer_cert, auth_str):
            return Response(content=f'{{"{Constants.ERROR_MESSAGE}": "WIP"}}', status_code=403)

        return await call_next(request)

class HttpProvider(BaseProvider, protocol=Constants.PROTOCOL_HTTP):
    def __init__(
            self,
            cafile: str,
            app_name: str = '',
    ):
        self.app = FastAPI()
        self.cafile = cafile
        self.policy_map = {}

    def add_provided_service(self, rule: RegistrationRule, ) -> None:
        self.policy_map[rule.service_uri] = rule

        self.app.add_api_route(
                path=rule.service_uri,
                endpoint=rule.func,
                methods=[rule.method],
        )

    def run_forever(
            self,
            address: str,
            port: int,
            keyfile: str,
            certfile: str,
    ):
        self.app.add_middleware(ArrowheadAccessPolicyMiddleware, policy_map=self.policy_map)

        uvicorn.run(
                self.app,
                host=address,
                port=port,
                ssl_keyfile=keyfile,
                ssl_certfile=certfile,
                ssl_ca_certs=self.cafile,
        )
