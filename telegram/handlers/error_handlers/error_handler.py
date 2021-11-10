import logging
from aiogram import types
import traceback


class ErrorHandler:
    def __init__(self, update, message_answer='Возникла ошибка, мы работаем над исправлением!'):
        self.update = update
        self.message_answer = message_answer

    def log_error(self):
        logging.error(f'Возникла непредвиденная ошибка:')
        logging.error(f'ИЗ-ЗА ЧЕГО: \n{self.update}')
        logging.error(f'ГДЕ: \n{traceback.format_exc()}')

    async def notify_user(self):
        try:
            await self.update.message.answer(self.message_answer)
        except AttributeError:
            await self.update.callback_query.message.answer(self.message_answer)

    @classmethod
    async def handle_error(cls, update: types.Update, exception: str):
        error_handler = cls(update)
        error_handler.log_error()
        await error_handler.notify_user()
        return True





