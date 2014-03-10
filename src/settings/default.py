DATABASES = {
    'NAME': 'example',
    'USER': 'mydatabaseuser',
    'PASSWORD': 'mypassword',
    'HOST': '127.0.0.1',
    'PORT': '5432',
    'SCHEMA': 'tq'
}

GEARMAN = {
    'PERSISTENT': {
        'hosts': ['localhost:4730', 'localhost:4731'],
        'waiting_timeout': 5
    },
    'VOLATILE': {
        'hosts': ['localhost:4730', 'localhost:4731'],
        'waiting_timeout': 5
    }
}

GEARMAN_RETRY_TIMEOUT = 5
GEARMAN_RECONNECT_TIMEOUT = 10
WAIT_DB_RESPONSE = 2

DEBUG = False

import logging

LOGGING = {
    'format': u'%(asctime)-15s: %(levelname)s: %(filename)s:%(lineno)d: %(message)s',
    'level': logging.DEBUG
}
