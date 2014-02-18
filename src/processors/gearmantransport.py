from base import BaseProcessor
from interfaces.gearman import GearmanAdapter
import logging


class GearmanTransport(BaseProcessor):
    """ Processor for realisation gearman transport from
    postgres
    """
    def __init__(self):
        """ Processor uses gearman adapter to rule the locks
        and concurrency races
        """
        self._gearman_client = GearmanAdapter()
        logging.debug("{name}: processor successfully initiated".format(
            name=self.__class__
        ))

    def callback(self, id, payload):
        """ This method just send task id and payload to
        gearman adapter queue
        """
        self._gearman_client.send(
            id,
            payload
        )

        logging.debug("{name}: task with id = {id} was sent to gearman client".format(
            name=self.__class__,
            id=id
        ))