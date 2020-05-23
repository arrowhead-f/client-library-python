import unittest
from arrowhead_client.service import ConsumedHttpService

class TestConsumedHttpService(unittest.TestCase):

    """Test case docstring."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_can_instantiate(self):
        test = ConsumedHttpService('', '', '', '', '', '', [''])

        with self.assertRaises(TypeError):
            test2 = ConsumedHttpService('', '', '', '', '', '')

if __name__ == "__main__":
    unittest.main()
