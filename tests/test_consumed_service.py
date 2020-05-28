import unittest
import requests
from arrowhead_client.service import ConsumedHttpService

class TestConsumedHttpService(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_can_instantiate(self):
        test = ConsumedHttpService('test_service', 'test', 'HTTP-SECURE-JSON', '127.0.0.1', '2345', requests.get)

if __name__ == "__main__":
    unittest.main()
