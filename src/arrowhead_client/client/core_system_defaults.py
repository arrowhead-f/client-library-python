from arrowhead_client import constants

_default_address = '127.0.0.1'

default_config = {
    'service_registry': {
        'system_name': constants.CoreSystem.SERVICE_REGISTRY,
        'address': _default_address,
        'port': 8443,
    },
    'orchestrator': {
        'system_name': constants.CoreSystem.ORCHESTRATOR,
        'address': _default_address,
        'port': 8441,
    },
    'authorization': {
        'system_name': constants.CoreSystem.AUTHORIZATION,
        'address': _default_address,
        'port': 8445,
    },
    'event_handler': {
        'system_name': constants.CoreSystem.EVENT_HANDLER,
        'address': _default_address,
        'port': 8455,
    },
    'gatekeeper': {
        'system_name': 'gatekeeper',
        'address': _default_address,
        'port': 8449,
    },
    'gateway': {
        'system_name': 'gatekeeper',
        'address': _default_address,
        'port': 8453,
    },
}

config = default_config
