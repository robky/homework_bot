import logging
import os
import requests
import time
from dotenv import load_dotenv
from exceptions import ConstantMissingError, EndpointStatusError
from http import HTTPStatus
from log_conf import logger
from telegram import Bot
from telegram.error import InvalidToken, Unauthorized
from typing import Union

logging.getLevelName("debug")
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


def send_message(bot: Bot, message: str) -> None:
    """Отправить сообщение в телеграмм."""
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


def get_api_answer(timestamp: int) -> dict:
    """Получить информацию от endpoint на указанную дату."""
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params)
    except Exception as error:
        logger.error(f'Ошибка эндпоинта -> {error}')
        raise ConnectionError(
            (
                f'Во время подключения к эндпоинту {ENDPOINT} произошла'
                f' непредвиденная ошибка: {error}'
                f' params = {params}'
            )
        ) from error
    status = homework_statuses.status_code
    if status == HTTPStatus.OK:
        return homework_statuses.json()
    else:
        raise EndpointStatusError(status)


def check_response(response: Union[list, dict]) -> list:
    """Выбрать значения 'homeworks' из полученных данных."""
    key = 'homeworks'
    if isinstance(response, list):
        response = response[0]
    key_value = response.get(key)
    if key_value is None:
        raise KeyError(key)
    if not isinstance(key_value, list):
        key_value = []
    return key_value


def first_work(response) -> str:
    """Получить информацию по последней работе."""
    homeworks = check_response(response)
    if homeworks:
        homework_name = homeworks[0].get('homework_name')
        homework_status = homeworks[0].get('status')
        date = homeworks[0].get('date_updated')
        verdict = HOMEWORK_STATUSES[homework_status]
        message = (f'Последнее событие: {date}, работы "{homework_name}". '
                   f'{verdict}')
    else:
        message = 'Нет информации по предыдущим работам'
    return message


def parse_status(homework: dict) -> str:
    """Получить информацию статуса работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверить наличие необходимых значений."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def get_bot() -> Bot:
    """Получить экземпляр Bot."""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
    except InvalidToken:
        logger.critical('Ошибка, некорректный TELEGRAM_TOKEN')
        raise SystemExit(1)
    except Exception as err:
        logger.error(f'Ошибка бота -> {err}')
        raise SystemExit(1)
    return bot


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = ('Отсутствует обязательная переменная окружения. '
                   'Программа принудительно остановлена.')
        logger.critical(message)
        raise ConstantMissingError('Отсутствует обязательная переменная')

    bot = get_bot()
    message = 'Начало работы'
    send_message(bot, message)

    current_timestamp = 0
    while True:
        try:
            if not current_timestamp:
                response = get_api_answer(current_timestamp)
                if response:
                    message = first_work(response)
                    send_message(bot, message)
                    current_timestamp = response.get('current_date')

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

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
