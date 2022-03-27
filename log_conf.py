import logging.config
import os

from dotenv import load_dotenv
from log_handler import TelegramHandler

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

ERROR_LOG_FILENAME = 'errors.log'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'stream_format': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        },
        'telegram_format': {
            'format': '%(levelname)s: %(message)s',
        },
    },

    'handlers': {
        'stream_handler': {
            'formatter': 'stream_format',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'telegram_handler': {
            'formatter': 'telegram_format',
            'level': 'ERROR',
            'class': 'log_handler.TelegramHandler',
            'token': TELEGRAM_TOKEN,
            'chat_id': TELEGRAM_CHAT_ID,
        },
    },

    'loggers': {
        'my_logger': {
            'handlers': [
                'stream_handler',
                # 'telegram_handler'
            ],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('my_logger')
