from gevent import monkey; monkey.patch_all()
import logging
from logging.config import dictConfig
import settings

dictConfig(settings.LOGGING)


def start_demon(obj):
    """ Demon start function. In general case demon has
    two listeners which listens notifications from postgres
    and processes deleting queries
    """
    from interfaces.db import Connect
    Connect().start(obj())


try:
    from interfaces.options import OPTIONS
    from importlib import import_module
    from interfaces.jobs import JobWrapper

    module = import_module("processors.{}".format(OPTIONS.processor.lower()))

    if not hasattr(module, OPTIONS.processor):
        raise KeyError("Can't find pointed processor")

    processor_cls = getattr(module, OPTIONS.processor)

    start_demon(processor_cls)
    #all spawned jobs before this string are joined in one waiter
    JobWrapper.join_all()
except KeyboardInterrupt, e:
    logging.debug("Demon shutdown")
    JobWrapper.kill_all()
except Exception, e:
    logging.error(e)
    raise e