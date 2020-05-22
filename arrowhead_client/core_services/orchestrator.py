#!/usr/bin/env python

from typing import Optional
import requests
from ..service import ConsumedHttpService
from ..configuration import default_config as config
from ..core_service_responses import handle_orchestration_response

_orchestrator = config['orchestrator']

services = {'orchestration-service': ConsumedHttpService(
            service_definition='orchestration-service',
            service_uri='orchestrator/orchestration',
            interface='HTTP-SECURE-JSON',
            address=_orchestrator['address'],
            port=_orchestrator['port'],
            http_method=requests.post,
            post_processing=handle_orchestration_response)}
