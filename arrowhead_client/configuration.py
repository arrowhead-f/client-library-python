#!/usr/bin/env python

from typing import Dict

default_config = {
    'service_registry': {'address': '127.0.0.1', 'port': '8443'},
    'orchestrator': {'address': '127.0.0.1', 'port': '8441'},
    'eventhandler': {'address': '127.0.0.1', 'port': '8455'},
    'gatekeeper': {'address': '127.0.0.1', 'port': '8449'},
    'gateway': {'address': '127.0.0.1', 'port': '8453'}, }


def set_config() -> Dict[str, Dict[str, str]]:
    return default_config
