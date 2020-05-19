from copy import deepcopy
from .orchestrator import services as orch_services
from .service_registry import services as sr_services
from ..service import ConsumedHttpService

all_core_services = {**sr_services, **orch_services}


def core_service(requested_service: str) -> ConsumedHttpService:
    core_service_instance = deepcopy(all_core_services.get(requested_service, None))

    if not core_service_instance:
        raise ValueError(f'Core service \'{requested_service}\' not found, '
                         f'available core services are {list(all_core_services.keys())}')

    return core_service_instance
