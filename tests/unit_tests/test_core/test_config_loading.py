import pytest

from arrowhead_client.client.implementations import SyncClient
# TODO: Write proper test using pytest.tmp_path and plaintext keyfile, certfile, and cafile
def test_from_yaml():
    client = SyncClient.from_config('tests/test_core/client.yaml')

    assert client.system_name == 'test_system'
    assert client.address == '127.0.0.1'
    assert client.port == 123456
    assert client.keyfile == "certificates/test.key"
    assert client.certfile == "certificates/test.crt"
    assert client.cafile == "certificates/sysop.ca"
