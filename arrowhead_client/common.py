from enum import Enum

class Constants(str, Enum):
    # Security modes
    SECURITY_INSECURE = 'INSECURE'
    SECURITY_SECURE = 'SECURE'
    # Access policies
    POLICY_UNRESTRICTED = 'NOT_SECURE'
    POLICY_CERTIFICATE = 'CERTIFICATE'
    POLICY_TOKEN = 'TOKEN'
    # Protocols:
    PROTOCOL_HTTP = 'HTTP'
    PROTOCOL_WS = 'WS'
    # HTTP methods:
    HTTP_METHOD_GET = 'GET'
    HTTP_METHOD_POST = 'POST'
    HTTP_METHOD_PUT = 'PUT'
    HTTP_METHOD_DELETE = 'DELETE'
    # Payload types
    PAYLOAD_JSON = 'JSON'
    PAYLOAD_TEXT = 'TEXT'

