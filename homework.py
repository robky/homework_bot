import logging
import os
import requests
import time
from dotenv import load_dotenv
from exceptions import (DictKeyDoesNotExistError, EndpointStatusError,
                        ConstantMissingError)
from http import HTTPStatus
from log_conf import logger
from telegram import Bot
from telegram.error import InvalidToken, Unauthorized
from typing import Union


load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses3/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: Bot, message: str) -> None:
    try:
        bot.send_message(
            TELEGRAM_CHAT_ID,
            message
        )
    except Unauthorized:
        logger.critical('Ошибка авторизации, проверьте TELEGRAM_TOKEN')
        raise SystemExit(1)
    except Exception as err:
        logger.error(f'Сообщение "{message}" не отправлено -> {err}')
    else:
        logger.info(f'Бот отправил сообщение "{message}"')


def get_api_answer(timestamp: int) -> Union[dict, bool]:
    params = {'from_date': timestamp}
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
        raise EndpointStatusError(status)


def check_response(response: Union[list, dict]) -> list:
    key = 'homeworks'
    if isinstance(response, list):
        response = response[0]
    key_value = response.get(key)
    if key_value is None:
        raise DictKeyDoesNotExistError(key)
    if not isinstance(key_value, list):
        key_value = []
    return key_value


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
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise ConstantMissingError()

    current_timestamp = 0
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
    except InvalidToken:
        logger.critical('Ошибка, некорректный TELEGRAM_TOKEN')
        raise SystemExit(1)
    except Exception as err:
        logger.error(f'Ошибка бота -> {err}')
        raise SystemExit(1)

    message = 'Начало работы'
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
                        send_message(bot, message)
                else:
                    logger.debug('Отсутствие в ответе новых статусов')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
