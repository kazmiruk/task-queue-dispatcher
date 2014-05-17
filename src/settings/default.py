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
        'waiting_timeout': 10
    },
    'VOLATILE': {
        'hosts': ['localhost:4730', 'localhost:4731'],
        'waiting_timeout': 10
    }
}

GEARMAN_RETRY_TIMEOUT = 10
GEARMAN_RECONNECT_TIMEOUT = 10
WAIT_DB_RESPONSE = 10

DEBUG = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'console': {
            'format': u'%(asctime)-15s: %(levelname)s: %(filename)s:%(lineno)d: %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': 'udp://c01073c86dd84fe28eccc363374245d6:d0630bf10200461f92bf75f7995a89a2@sentry.dev.pearbox.net:9001/6'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}