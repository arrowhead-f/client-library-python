"""
================
Constants module
================

A central repository for the constants used throughout the library.
Can be used by both internal and external users, though external users might prefer to just use strings instead.
"""
from enum import Enum, Flag, auto


class Security(str, Enum):
    """Security Modes"""
    INSECURE = 'INSECURE'
    SECURE = 'SECURE'


class AccessPolicy(str, Enum):
    """Access policies"""
    UNRESTRICTED = 'NOT_SECURE'
    CERTIFICATE = 'CERTIFICATE'
    TOKEN = 'TOKEN'


class Protocol(str, Enum):
    """Protocols"""
    HTTP = 'HTTP'
    WS = 'WS'


class HttpMethod(str, Enum):
    """HTTP methods"""
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class Payload(str, Enum):
    """Payload types"""
    JSON = 'JSON'
    TEXT = 'TEXT'


class CoreSystem(str, Enum):
    """Core systems"""
    SERVICE_REGISTRY = 'service_registry'
    ORCHESTRATOR = 'orchestrator'
    AUTHORIZATION = 'authorization'
    EVENT_HANDLER = 'event_handler'

class OrchestrationFlags(Flag):
    MATCHMAKING = auto()
    METADATA_SEARCH = auto()
    ONLY_PREFERRED = auto()
    PING_PROVIDERS = auto()
    OVERRIDE_STORE = auto()
    ENABLE_INTER_CLOUD = auto()
    TRIGGER_INTER_CLOUD = auto()


class Misc(str, Enum):
    """Auxiliary constants"""
    ERROR_MESSAGE = 'errorMessage'
