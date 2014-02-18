import gearman
import settings
from json import dumps
import logging


class Client(object):
    """ Low-level client for gearman. You shouldn't
    use it directly
    """
    persistent_client = None
    volatile_client = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Client, cls).__new__(cls)
        return cls.instance

    def reset(self):
        """ resets cached sockets
        """
        self.persistent_client = None
        self.volatile_client = None
        logging.debug("Gearman cache reseted")

    def _get_client(self, persistent):
        """ get persistent or volatile gearman storage
        and cached it in memory
        """
        if persistent:
            if not self.persistent_client:
                self.persistent_client = gearman.GearmanClient(
                    settings.GEARMAN['PERSISTENT']['hosts']
                )

            client = self.persistent_client
            reconnect_timeout = settings.GEARMAN['PERSISTENT']['reconnect_timeout']
        else:
            if not self.volatile_client:
                self.volatile_client = gearman.GearmanClient(
                    settings.GEARMAN['VOLATILE']['hosts']
                )

            client = self.volatile_client
            reconnect_timeout = settings.GEARMAN['VOLATILE']['reconnect_timeout']

        return client, reconnect_timeout

    def send(self, object_info, task_type, persistent=False):
        """ sends object into task_type queue
        """
        client, reconnect_timeout = self._get_client(persistent)

        logging.debug("{task_type} was sent to gearman".format(
            task_type=task_type
        ))

        return client.submit_job(
            task_type,
            dumps(object_info),
            background=True,
            wait_until_complete=True,
            poll_timeout=reconnect_timeout
        )

    def is_available(self, persistent=True):
        """ Ping all of the hosts, that defined in the settings,
            and return True if one of them is available.
        """
        if persistent:
            hosts = settings.GEARMAN['PERSISTENT']['hosts']
        else:
            hosts = settings.GEARMAN['VOLATILE']['hosts']

        for host in hosts:
            try:
                client = gearman.admin_client.GearmanAdminClient([host, ])
                client.ping_server()
                return True
            except gearman.errors.ServerUnavailable:
                # try next gearman host
                pass

        return False
