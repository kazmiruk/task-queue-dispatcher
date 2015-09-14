import mock

import gearman

import unittest
from interfaces.gearman.client import Client


class TestGearmanInterfaces(unittest.TestCase):
    def test_gearman_client_singleton(self):
        self.assertEqual(Client(), Client())

    def test_gearman_is_available(self):
        client = Client()

        self.assertTrue(client.is_available())

    def test_reconnect_gearman_after_timeout_error(self):
        client = Client()

        def failed_ping_server(*args):
            raise gearman.errors.InvalidAdminClientState()

        with mock.patch("interfaces.gearman.client.gearman.GearmanAdminClient.ping_server", failed_ping_server):
            self.assertFalse(client.is_available())
