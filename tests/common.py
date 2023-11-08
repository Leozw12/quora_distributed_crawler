import unittest
from utils import check_port, check_connect


class TestCommon(unittest.TestCase):
    def test_check_port(self):
        result = check_port.check(8000)
        self.assertFalse(result, 'Port 800 is unavailable.')

    def test_check_connect(self):
        result = check_connect.is_connectable()
        self.assertTrue(result, 'Unable to connect to www.quora.com.')
