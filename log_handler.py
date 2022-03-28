from telegram import Bot
from logging import Handler, LogRecord


class TelegramHandler(Handler):
    def __init__(self, token: str, chat_id: str):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.last_error = ''

    def emit(self, record: LogRecord):
        if record.msg != self.last_error and self.token and self.chat_id:
            try:
                bot = Bot(token=self.token)
                bot.send_message(
                    self.chat_id,
                    self.format(record)
                )
            except Exception as err:
                print(f'Bot не смог отправить сообщение -> {err}')
            else:
                self.last_error = record.msg
                print(f'Бот отправил сообщение "{self.last_error}"')
