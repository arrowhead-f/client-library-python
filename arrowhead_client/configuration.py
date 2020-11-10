from arrowhead_client.system import ArrowheadSystem
_default_address = '127.0.0.1'

default_config = {
    'service_registry':
        ArrowheadSystem(
                'service_registry',
                _default_address,
                8443,
                '', ),
    'orchestrator':
        ArrowheadSystem(
                'orchestrator',
                _default_address,
                8441,
                '', ),
    'eventhandler':
        ArrowheadSystem(
                'eventhandler',
                _default_address,
                8455,
                '', ),
    'gatekeeper':
        ArrowheadSystem(
                'gatekeeper',
                _default_address,
                8449,
                '', ),
    'gateway':
        ArrowheadSystem(
                'gatekeeper',
                _default_address,
                8453,
                '', )
}

config = default_config
