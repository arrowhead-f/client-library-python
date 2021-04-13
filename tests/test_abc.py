from contextlib import nullcontext
from abc import ABC

import pytest

from arrowhead_client import abc

PROTOCOL_PARAMETERS = (
    ('html', nullcontext()),
    ('', pytest.raises(ValueError)),
    (None, pytest.raises(TypeError)),
    (1234, pytest.raises(TypeError)),
)

@pytest.mark.parametrize('protocol, expectation', PROTOCOL_PARAMETERS)
def test_protocol_subclassing(protocol, expectation):
    with expectation:
        class Test(abc.ProtocolMixin, protocol=protocol):
            pass

@pytest.mark.parametrize('protocol, expectation', PROTOCOL_PARAMETERS)
def test_protocol_double_subclassing(protocol, expectation):
    with expectation:
        class TestBase(abc.ProtocolMixin, ABC, protocol='<PROTOCOL>'):
            pass

        class Test(TestBase, protocol=protocol):
            pass

@pytest.mark.parametrize('protocol', ({'html'}, {'HTML'}))
def test_protocol_uppercase(protocol):
    class Test(abc.ProtocolMixin, protocol=protocol):
        pass

    test = Test()

    assert Test._protocol <= {prot.upper() for prot in protocol}
    assert test._protocol <= {prot.upper() for prot in protocol}

