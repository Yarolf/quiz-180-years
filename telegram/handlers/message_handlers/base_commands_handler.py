from aiogram import types
import logging
from . import registration_handler


async def process_start_command(message: types.Message):
    logging.info(f'{message.from_user.first_name} {message.from_user.last_name} ввёл команду start')
    await registration_handler.process_register_command(message)


async def process_help_command(message: types.Message):
    await message.answer("""
    Список доступных команд:
    /about - информация о боте
    /register - зарегистрироваться
    /update_info - обновить данные профиля
    /test - пройти викторину""")


async def process_about_command(message: types.Message):
    await message.answer('Добрый день! Это бот для прохождения викторины, посвященной 180 летию Сбера!')
