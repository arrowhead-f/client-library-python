from fastapi import FastAPI, Request

from arrowhead_client.abc import BaseProvider
from arrowhead_client.common import Constants
from arrowhead_client.rules import RegistrationRule

class HttpProvider(BaseProvider, protocol=Constants.PROTOCOL_HTTP):
    def __init__(
            self,
            cafile: str,
            app_name: str = '',
    ):
        self.app = FastAPI()
        self.cafile = cafile

    def add_provided_service(self, rule: RegistrationRule, ) -> None:
        def func_with_access_policy():
            pass
