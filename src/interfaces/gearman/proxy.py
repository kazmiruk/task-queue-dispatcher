from gevent.queue import Queue
from client import Client
from gevent import sleep
import settings
from interfaces.db.proxy import SUCCESS_QUEUE
from interfaces.jobs import JobWrapper
import logging

SEND_QUEUE = Queue(maxsize=None)
ERROR_QUEUE = Queue(maxsize=None)


class Proxy(object):
    """ Async proxy for gearman notifications
    """
    def __init__(self):
        """ Starts sender and error listener
        """
        self._client = Client()

        JobWrapper.start_listen(self._sender_loop)
        JobWrapper.start_listen(self._error_loop)

    def send(self, id, payload):
        """ sending task into gearman just add it to
        the async queue
        """
        logging.debug("Add task {id} into send queue".format(
            id=id
        ))
        payload['id'] = id
        SEND_QUEUE.put(payload)

    def _sender_loop(self):
        """ sender loop method get task from queue and try
        to send it into gearman. If it fails then task goes
        to the error queue and wait there GEARMAN_RETRY
        """
        obj = SEND_QUEUE.get()

        while not self._client.is_available(obj['persistent']):
            logging.error("Gearman not available for {persistent}".format(
                persistent=obj['persistent']
            ))

            sleep(settings.GEARMAN_RETRY)

        gearman_send_status = self._client.send(
            obj['data'],
            str(obj['gearman_queue_name']),
            obj['persistent']
        )

        if gearman_send_status:
            logging.debug("Task {id} was successfully sent".format(
                id=obj['id']
            ))
            SUCCESS_QUEUE.put(obj['id'])
        else:
            logging.debug("Task {id} was returned to error queue".format(
                id=obj['id']
            ))
            ERROR_QUEUE.put(obj)

        return True

    def _error_loop(self):
        """ Method spawns task with errors into
        other green thread
        """
        obj = ERROR_QUEUE.get()
        JobWrapper.spawn(self._error_delay, obj)

    def _error_delay(self, obj):
        """ method sleeps GEARMAN_RETRY time and then
        send task into queue to retry send it
        """
        logging.debug("Task {id} will be sleep {second} seconds".format(
            id=obj['id'],
            second=settings.GEARMAN_RETRY
        ))
        sleep(settings.GEARMAN_RETRY)
        SEND_QUEUE.put(obj)