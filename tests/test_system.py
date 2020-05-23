import unittest
from arrowhead_client.system import ArrowheadSystem

class TestArrowheadSystem(unittest.TestCase):
    def setUp(self):
        self.test_system = ArrowheadSystem('test_system', '127.0.0.1', 1234, 'abc123')

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(self.test_system.system_name, 'test_system')
        self.assertEqual(self.test_system.address, '127.0.0.1')
        self.assertEqual(self.test_system.port, 1234)
        self.assertEqual(self.test_system.authentication_info, 'abc123')

    def test_url(self):
        self.assertEqual(self.test_system.url, '127.0.0.1:1234')

    def test_dto(self):
        true_dto = {
            'systemName': 'test_system',
            'address': '127.0.0.1',
            'port': 1234,
            'authenticationInfo': 'abc123'
        }
        self.assertEqual(self.test_system.dto, true_dto)
