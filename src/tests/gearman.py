import unittest
from interfaces.gearman.client import Client


class TestGearmanInterfaces(unittest.TestCase):
    def test_gearman_client_singleton(self):
        self.assertEqual(Client(), Client())

    def test_gearman_is_available(self):
        client = Client()

        self.assertTrue(client.is_available())