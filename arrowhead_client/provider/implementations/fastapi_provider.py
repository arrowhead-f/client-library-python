from typing import Mapping, Dict, Callable
import json

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn  # type: ignore

from arrowhead_client.provider.base import BaseProvider
from arrowhead_client.rules import RegistrationRule
from arrowhead_client.security.access_policy import TokenAccessPolicy
from arrowhead_client import constants


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
        if path not in self.policy_map:
            return await call_next(request)
        # TODO: Replace these with actual request values when uvicorn implements client-certs or when you try running a reverse proxy
        consumer_cert = 'consumer_cert'
        auth_str = 'auth_str'

        if isinstance(self.policy_map[path].access_policy, TokenAccessPolicy):
            return Response(content=json.dumps({constants.Misc.ERROR_MESSAGE: 'Token access policy not supported'}),
                            status_code=501)
        if not self.policy_map[path].is_authorized(consumer_cert, auth_str):
            return Response(content=f'{{"{constants.Misc.ERROR_MESSAGE}": "WIP"}}', status_code=403)

        return await call_next(request)


class FastapiProvider(BaseProvider, protocol=constants.Protocol.HTTP):
    def __init__(
            self,
            cafile: str,
            app_name: str = '',
    ):
        super().__init__(cafile)
        self.app = FastAPI()
        self.policy_map: Dict[str, RegistrationRule] = {}

    def add_provided_service(self, rule: RegistrationRule, ) -> None:
        self.policy_map[rule.service_uri] = rule

        if rule.protocol == constants.Protocol.HTTP:
            self.app.add_api_route(
                    path=f'/{rule.service_uri}',
                    endpoint=rule.func,
                    methods=[rule.method],
            )
        elif rule.protocol == constants.Protocol.WS:
            self.app.add_api_websocket_route(
                    path=f'/{rule.service_uri}',
                    endpoint=rule.func,
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

    def add_startup_routine(self, func: Callable):
        self.app.add_event_handler('startup', func)

    def add_shutdown_routine(self, func: Callable):
        self.app.add_event_handler('shutdown', func)
