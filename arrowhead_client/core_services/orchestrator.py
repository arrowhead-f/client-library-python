from typing import Dict
from .. import backend
from ..service import ConsumedHttpService
from ..configuration import default_config as config
from ..core_service_responses import handle_orchestration_response

_orchestrator = config['orchestrator']

services: Dict[str, ConsumedHttpService] = {'orchestration-service': ConsumedHttpService(
            service_definition='orchestration-service',
            service_uri='orchestrator/orchestration',
            interface='HTTP-SECURE-JSON',
            address=_orchestrator['address'],
            port=_orchestrator['port'],
            http_method=backend.post,
            post_processing=handle_orchestration_response)}
