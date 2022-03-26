import logging
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

from exceptions import ConstantMissingError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Здесь задана глобальная конфигурация для всех логгеров
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# А тут установлены настройки логгера для текущего файла - example_for_log.py
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.DEBUG)
# Указываем обработчик логов
# handler = logging.StreamHandler()
# logger.addHandler(handler)
# Создаем форматер
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# Применяем его к хэндлеру
# handler.setFormatter(formatter)

data_token_const = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
                    'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
                    'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID}
NEXT_TIME_SECOND = 5 * 60 * 60 + 1
data_var = {'timestamp': 0}


def send_message(bot, message):
    ...


def get_api_answer(timestamp: int) -> dict:
    params = {'from_date': timestamp}
    # Делаем GET-запрос к эндпоинту с заголовком headers и параметрами params
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params)
    except Exception as err:
        logger.error(f'Ошибка эндпоинта -> {err}')
        return {}
    return homework_statuses.json()


def check_response(response: dict):
    return response.get('homeworks', None)


def parse_status(homework: dict):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
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
    logger.info(f'Начало работы')
    check_tokens()
    current_timestamp = 1

    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    ...

    while True:
        try:
            if not current_timestamp:
                response = get_api_answer(current_timestamp)
                if response:
                    homeworks = check_response(response)
                    if homeworks:
                        last_time = homeworks[0].get('date_updated')
                        d = datetime.strptime(last_time, "%Y-%m-%dT%H:%M:%SZ")
                        current_timestamp = int(
                            time.mktime(d.timetuple())) + NEXT_TIME_SECOND
                    else:
                        current_timestamp = response.get('current_date')
                    logger.info(f'Начальная точка '
                                f'timestamp={current_timestamp}')
            response = get_api_answer(current_timestamp)
            if response:
                current_timestamp = response.get('current_date')
                homeworks = check_response(response)
                if homeworks:
                    for homework in homeworks:
                        message = parse_status(homework)
                        logger.info(message)
                else:
                    logger.info(f'Cобытий нет, current_timestamp={current_timestamp}')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
