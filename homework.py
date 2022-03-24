import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import ConstantMissingError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

log_format = '%(asctime)s [%(levelname)s] %(message)s'
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)

data_token_const = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
                    'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
                    'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID}
data_var = {'timestamp': 0}


def send_message(bot, message):
    ...


def get_api_answer(current_timestamp: time = data_var['timestamp']):
    # timestamp = current_timestamp or int(time.time())
    params = {'from_date': current_timestamp}
    # Делаем GET-запрос к эндпоинту с заголовком headers и параметрами params
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return homework_statuses.json()
    '''
    Логика: запрашиваем в первый раз с нулевого времени - получаем все работы,
    берем время последний плюсуем 1, и уже с этого времени следим за 
    изменениями
    '''


def check_response(response):
    ...


def parse_status(homework):
    homework_name = ...
    homework_status = ...
    ...

    verdict = ...
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    for token_name, value in data_token_const.items():
        if not value:
            message = ('Отсутствие обязательных переменных окружения во время '
                       'запуска бота')
            logger.critical(message)
            raise ConstantMissingError(token_name, message)
    return True


def main():
    """Основная логика работы бота."""
    check_tokens()

    #data_var.setdefault('time', 1)
    print(get_api_answer())

    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    ...

    while False:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
