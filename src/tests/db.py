import unittest
import settings
from gdbpool.interaction_pool import DBInteractionPool
from interfaces.db.proxy import Proxy


class TestDBInterfaces(unittest.TestCase):
    def get_connection(self, poll_connections):
        dsn = "host={host} port={port} user={user} password={password} dbname={dbname}".format(
            host=settings.DATABASES['HOST'],
            port=settings.DATABASES['PORT'],
            user=settings.DATABASES['USER'],
            password=settings.DATABASES['PASSWORD'],
            dbname=settings.DATABASES['NAME']
        )

        return DBInteractionPool(dsn, pool_size=poll_connections, do_log=settings.DEBUG)

    def test_connection(self):
        poll_connections = 2
        ipoll = self.get_connection(poll_connections)

        self.assertEqual(ipoll.conn_pools['default'].qsize, poll_connections)

    def test_query(self):
        poll_connections = 2
        ipoll = self.get_connection(poll_connections)

        result = ipoll.run("SELECT 1 as ret")
        rows = result.get(block=True)

        self.assertIsInstance(rows, list)
        self.assertIsInstance(rows[0]['ret'], int)

    def test_parse_time_less(self):
        current_time = '2014-02-02 10:00:00'
        seconds = Proxy._sked_time2seconds(current_time)

        self.assertEqual(seconds, 0)

    def test_parse_time_more(self):
        current_time = '2074-02-02 10:00:00'
        seconds = Proxy._sked_time2seconds(current_time)

        self.assertLess(0, seconds)