from gdbpool.interaction_pool import DBInteractionPool
from interfaces.options import OPTIONS
import gevent
from interfaces.jobs import JobWrapper
import settings
import logging


class DBConnection(object):
    """ Low level adapter for interaction with postgres
    queries and notifications
    """
    def __init__(self, host, port, dbname, user, password, schema):
        """ Connection to databases use dsn for opening async
        socket. Each demon uses two connections: for notifier and
        queries
        """
        dsn = DBConnection._get_dsn(host, port, dbname, user, password)

        self._ipoll = DBInteractionPool(dsn, pool_size=2, do_log=settings.DEBUG)
        self._schema = schema

    @staticmethod
    def _get_dsn(host, port, dbname, user, password):
        """ generating dsn from set of vars
        """
        return "host={host} port={port} user={user} password={password} dbname={dbname}".format(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )

    def _get_collection_name(self):
        """ generates path (schema and table name) to the queue
        collection
        """
        return "{schema}.{channel_name}".format(
            schema=self._schema,
            channel_name=self._channel_name()
        )

    def _channel_name(self):
        """ generates channel name from queue name and chunk
        """
        return "{queue_name}_{chunk}".format(
            queue_name=OPTIONS.queue_name,
            chunk=OPTIONS.chunk
        )

    def _get_query(self, sql):
        """ generates query with collection name. Require placeholder
        data_path in query
        """
        return sql.format(
            data_path=self._get_collection_name()
        )

    def delete_row(self, object_id):
        """ Delete processed row from database. It has bug in AsyncResult which
        require some data to obtain from socket. Fro such purposes delete query
        has select postfix
        """
        result = self._ipoll.run(
            self._get_query("DELETE FROM {data_path} WHERE id = %s; SELECT 1 as status"),
            [object_id]
        )

        try:
            status = result.get(
                timeout=gevent.Timeout(settings.WAIT_DB_RESPONSE)
            )[0]['status']
        except gevent.Timeout, e:
            status = False

        logging.debug("Row from {collection_name} with id {id} deleted with status {status}".format(
            collection_name=self._get_collection_name(),
            id=object_id,
            status=status
        ))

        return status

    def select_all(self):
        """Selects all saved tasks in db. It calls only in the starting of
        demon
        """
        result = self._ipoll.run(
            self._get_query("SELECT id, payload, sked_time FROM {data_path}"),
            []
        )

        tasks = result.get()

        logging.debug("There are {count} rows save in db".format(
            count=len(tasks)
        ))

        return tasks

    def listen(self, rq):
        """ Listen one connection to obtain notifications
        from postgres
        """
        stop_event = gevent.event.Event()

        JobWrapper.spawn(
            self._ipoll.listen_on,
            result_queue=rq,
            channel_name=self._channel_name(),
            cancel_event=stop_event
        )

        logging.debug("Postgres notify listeners spawned")