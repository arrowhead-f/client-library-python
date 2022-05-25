import aiocoap
from aiocoap import resource

from arrowhead_client.provider.base import BaseProvider
from arrowhead_client.rules import RegistrationRule
from arrowhead_client.request import Request
from arrowhead_client import errors
from arrowhead_client import constants

class AioCoapProvider(BaseProvider, protocol='COAP'):

    def __init__(self, cafile: str = ''):
        super().__init__(cafile)
        self.app = resource.Site()

    def add_provided_service(self, rule: RegistrationRule, ) -> None:
        pass


