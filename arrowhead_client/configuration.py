_default_address = '127.0.0.1'

default_config = {
    'service_registry': {
                'system_name': 'service_registry',
                'address': _default_address,
                'port': 8443,
    },
    'orchestrator': {
                'system_name': 'orchestrator',
                'address': _default_address,
                'port': 8441,
    },
    'authorization': {
                'system_name': 'authorization',
                'address': _default_address,
                'port': 8445,
    },
    'eventhandler': {
                'system_name': 'eventhandler',
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
