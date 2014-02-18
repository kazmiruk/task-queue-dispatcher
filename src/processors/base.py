class BaseProcessor(object):
    """ Base class for implementing demon processors
    """
    def __init__(self):
        """ You should implement initiation of processor
        """
        raise NotImplementedError()

    def callback(self, id, payload):
        """ You should implement here queue dispatcher logic
        """
        raise NotImplementedError()