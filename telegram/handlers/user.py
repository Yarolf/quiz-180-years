from aiogram import types

from telegram.bot import dispatcher as dp
import logging


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'Пользователь {message.from_user.id} ввёл команду start')
    await message.answer('HI')
