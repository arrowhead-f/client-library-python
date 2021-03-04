from abc import ABC


class ProtocolMixin(ABC):
    def __init_subclass__(cls, protocol='', **kwargs):
        if protocol == '':
            raise ValueError('No protocol specified.')
        elif not isinstance(protocol, str):
            raise TypeError('Protocol must be of type str.')
        cls._protocol = protocol.upper()


