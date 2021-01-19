import pytest
import json

from arrowhead_client.response import Response

true_string = b'{"dummy": "data"}'

def test_init():
    response = Response(true_string, 'JSON', 200,)

    assert response.payload == true_string
    assert response.payload_type == 'JSON'
    assert response.status_code == 200

def test_good_json():
    response = Response(true_string, 'JSON', 200,)

    assert response.read_json() == {'dummy': 'data'}

def test_bad_json():
    response = Response(b'nthoenutheou', 'JSON', 200,)

    with pytest.raises(RuntimeError):
        assert response.read_json() is None

def test_string():
    response = Response(true_string, 'JSON', 200,)

    assert response.read_string() == '{"dummy": "data"}'
