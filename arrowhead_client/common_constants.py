from enum import Enum

class SecurityInfo(str, Enum):
    INSECURE = 'INSECURE'
    SECURE = 'SECURE'

class AccessPolicies(str, Enum):
    UNRESTRICTED = 'NOT_SECURE'
    CERTIFICATE = 'CERTIFICATE'
    TOKEN = 'TOKEN'