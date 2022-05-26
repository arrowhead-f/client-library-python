import pytest
from contextlib import nullcontext

from arrowhead_client import service
from arrowhead_client import constants

class TestServiceInterface:
    @pytest.mark.parametrize(
        'protocol, secure, payload',
        (
                ('HTTP', 'SECURE', 'JSON'),
                ('http', 'secure', 'json'),
        )
    )
    def test_interface_construction(self, protocol, secure, payload):
        test_interface = service.ServiceInterface(protocol, secure, payload)

        assert test_interface.protocol == protocol.upper()
        assert test_interface.secure == secure.upper()
        assert test_interface.payload == payload.upper()
        assert test_interface.dto() == f'{protocol}-{secure}-{payload}'.upper()
        assert test_interface == test_interface.dto()

    @pytest.mark.parametrize(
            'interface_string, expectation',
            (
                    ('HTTP-SECURE-JSON', nullcontext()),
                    ('http-secure-json', nullcontext()),
                    ('', pytest.raises(ValueError)),
                    ('TEST-TEST', pytest.raises(ValueError)),
                    ('TEST-TEST-TEST-TEST', pytest.raises(ValueError)),
            )
    )
    def test_interface_from_str(self, interface_string, expectation):
        split_interface = interface_string.split('-')

        with expectation:
            test_interface = service.ServiceInterface.from_str(interface_string)

            assert test_interface.protocol == split_interface[0].upper()
            assert test_interface.secure == split_interface[1].upper()
            assert test_interface.payload == split_interface[2].upper()

    @pytest.mark.parametrize('access_policy, secure',[
        (constants.AccessPolicy.UNRESTRICTED, constants.Security.INSECURE),
        (constants.AccessPolicy.CERTIFICATE, constants.Security.SECURE),
        (constants.AccessPolicy.TOKEN, constants.Security.SECURE),
    ])
    def test_interface_from_access_policy(self, access_policy, secure):
        test_interface = service.ServiceInterface.with_access_policy('HTTP', access_policy, 'JSON')

        assert test_interface.secure == secure

    def test_equality(self):
        test_interface = service.ServiceInterface('HTTP', 'SECURE', 'JSON')
        interface_string = 'HTTP-SECURE-JSON'

        assert test_interface == test_interface
        assert test_interface == interface_string
        assert interface_string == test_interface

        with pytest.raises(TypeError):
            assert 1 == test_interface