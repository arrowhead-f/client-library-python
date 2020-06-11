from typing import Dict
from arrowhead_client.service import Service


services: Dict[str, Service] = {'orchestration-service': Service(
            service_definition='orchestration-service',
            service_uri='orchestrator/orchestration',
            interface='HTTP-SECURE-JSON',)
}
