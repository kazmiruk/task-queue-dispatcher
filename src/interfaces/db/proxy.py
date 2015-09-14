import settings
from gevent.queue import Queue
import gevent
import json
from dateutil import parser
from datetime import datetime
from interfaces.jobs import JobWrapper
import logging

SUCCESS_QUEUE = Queue(maxsize=None)
NOTIFY_QUEUE = Queue(maxsize=None)


class Proxy(object):
    """ Singleton proxy adapter for async postgres
    adapter
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Proxy, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """ initiate local storage to caching queries and
        db pool
        """
        from client import DBConnection

        self.db = DBConnection(settings.DATABASES['HOST'], settings.DATABASES['PORT'],
                               settings.DATABASES['NAME'], settings.DATABASES['USER'],
                               settings.DATABASES['PASSWORD'], settings.DATABASES['SCHEMA'])

        self._local_list = {}
        self._processor = None

    def _select_current_tasks(self):
        """ selects current tasks from db and spawn
        processors. It runs only in the start
        """
        result = self.db.select_all()

        for row in result:
            row['payload'] = row['payload']

            self._local_list[row['id']] = {
                'payload': row['payload'],
                'sked_time': row['sked_time']
            }

            JobWrapper.spawn(self._set_sked_time_callback, row['id'], row['payload'], row['sked_time'])

    def start(self, processor):
        """ Method to start processing of demon logic
        """
        self._processor = processor

        # start success listener
        JobWrapper.start_listen(self._success_listener)

        # then selecting current unprocessed tasks
        self._select_current_tasks()
        # and only after that starts to listen notifications
        self.db.listen(NOTIFY_QUEUE)
        # and start listener to transport it to the processor
        JobWrapper.start_listen(self._task_listener)

    def get_row(self, id):
        """ proxy method to get row from db or cache
        """
        if id in self._local_list:
            return self._local_list[id]
        else:
            logging.warning("Try to obtain absent row with id {id}".format(id=id))
            return None

    def delete_row(self, id):
        """ deletes row from database and cache
        """
        if id not in self._local_list:
            logging.warning("Try to delete row {id} which absent in local storage".format(id=id))

        if self.db.delete_row(id):
            del self._local_list[id]
        else:
            logging.error("Error in query to databese while deleteing row with id {id}".format(id=id))

    def _set_sked_time_callback(self, id, payload, sked_time):
        """ green threed function for waiting sked time
        """
        seconds = Proxy._sked_time2seconds(sked_time)

        logging.debug("Greenlet will be sleep {second} seconds".format(second=seconds))
        gevent.sleep(seconds)

        self._processor.callback(id, payload)

    @staticmethod
    def _sked_time2seconds(ds):
        """ Converting sked_time to seconds
        """
        diff = 0

        if ds:
            if isinstance(ds, str) or isinstance(ds, unicode):
                ds = parser.parse(ds)

            ds_now = datetime.now(tz=getattr(ds, 'tzinfo', None))
            delta = ds - ds_now
            diff_local = delta.total_seconds()

            if diff_local > 0:
                diff = diff_local

        return diff

    def _task_listener(self):
        """ Task listener callback
        """
        data = self._repair_data(NOTIFY_QUEUE.get())

        self._local_list[data['id']] = {
            'payload': data['payload'],
            'sked_time': data['sked_time']
        }

        JobWrapper.spawn(self._set_sked_time_callback, data['id'],
                         data['payload'], data['sked_time'])

        return True

    def _repair_data(self, data):
        """ The GDBPool has strange bug which break object.
        This method fix it
        """
        # TODO: try to fix it in other way
        raw = ""

        for key in data:
            raw += "{key}:{value}".format(key=key, value=data[key])
        return json.loads(raw)

    def _success_listener(self):
        """ listener for successed tasks which spawns for
        deleting rows
        """
        task = SUCCESS_QUEUE.get()
        JobWrapper.spawn(self.delete_row, task)

        return True
