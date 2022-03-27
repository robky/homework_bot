import logging
import os
import time
from http import HTTPStatus
from pprint import pprint
from typing import Union
from telegram import Bot
import requests
from dotenv import load_dotenv

from exceptions import ConstantMissingError, EndpointStatusError
from log_conf import logger

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

NEXT_TIME_SECOND = 5 * 60 * 60 + 1
data_var = {'timestamp': 0}


def send_message(bot, message) -> None:
    try:
        bot.send_message(
            TELEGRAM_CHAT_ID,
            message
        )
    except Exception as err:
        logger.error(f'Сообщение не отправлено -> {err}')
    else:
        logger.info(f'Бот отправил сообщение "{message}"')


def get_api_answer(timestamp: int) -> Union[dict, bool]:
    params = {'from_date': timestamp}
    # Делаем GET-запрос к эндпоинту с заголовком headers и параметрами params
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params)
    except Exception as err:
        logger.error(f'Ошибка эндпоинта -> {err}')
        return False
    status = homework_statuses.status_code
    if status == HTTPStatus.OK:
        return homework_statuses.json()
    else:
        logger.critical(f'Ошибка эндпоинта, код статуса -> {status}')
        raise EndpointStatusError(status)


def check_response(response: dict):
    return response.get('homeworks')


def parse_first(homework: dict) -> str:
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    date = homework.get('date_updated')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Последнее событие: {date}, работы "{homework_name}". {verdict}'


def parse_status(homework: dict) -> str:
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    need_token_const = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
                        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
                        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID}
    for token_name, value in need_token_const.items():
        if not value:
            message = (f"Отсутствует обязательная переменная окружения: "
                       f"'{token_name}' Программа принудительно остановлена.")
            logger.critical(message)
            # raise ConstantMissingError(token_name, message)
            return False
    return True


def main():
    """Основная логика работы бота."""
    if check_tokens():
        current_timestamp = 0
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
        except Exception as err:
            logger.error(f'Ошибка бота -> {err}')
            bot = None

        message = 'Начало работы'
        logger.info(message)
        send_message(bot, message)

        while True:
            try:
                if not current_timestamp:
                    response = get_api_answer(current_timestamp)
                    if response:
                        homeworks = check_response(response)
                        if homeworks:
                            message = parse_first(homeworks[0])
                            current_timestamp = response.get('current_date')
                        else:
                            message = 'Нет информации по предыдущим работам'
                        send_message(bot, message)
                response = get_api_answer(current_timestamp)
                if response:
                    current_timestamp = response.get('current_date')
                    homeworks = check_response(response)
                    if homeworks:
                        for homework in homeworks:
                            message = parse_status(homework)
                            logger.info(message)
                    else:
                        logger.info(f'Cобытий нет, '
                                    f'current_timestamp={current_timestamp}')
                time.sleep(RETRY_TIME)

            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(message)
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
