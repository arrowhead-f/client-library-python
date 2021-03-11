from enum import Enum

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
    HTTP_METHOD_GET = 'GET'
    HTTP_METHOD_POST = 'POST'
    HTTP_METHOD_PUT = 'PUT'
    HTTP_METHOD_DELETE = 'DELETE'

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

class Misc(str, Enum):
    """Auxiliary constants"""
    ERROR_MESSAGE = 'errorMessage'
