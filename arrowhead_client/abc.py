from abc import ABC


class ProtocolMixin(ABC):
    def __init_subclass__(cls, protocol='', **kwargs):
        if protocol == '':
            raise ValueError('No protocol specified.')
        elif isinstance(protocol, set):
            if not all(isinstance(prot, str) for prot in protocol):
                raise ValueError('All protocols specified must be of type str')
            cls._protocol = set(prot.upper() for prot in protocol)
        elif isinstance(protocol, str):
            cls._protocol = {protocol.upper()}
        else:
            raise TypeError('protocol must be of type str or set')
