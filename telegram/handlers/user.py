from aiogram import types

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'Пользователь {message.from_user.id} ввёл команду start')
    await message.answer('Ваши данные сохранены')
    User.get_or_create(telegram_id=message.from_user.id,
                       first_name=message.from_user.first_name,
                       second_name=message.from_user.last_name,
                       nick_name=message.from_user.username)


@dp.message_handler(commands=['test'])
async def process_test_command(message: types.Message):
    question: QuestionBlock = QuestionBlock.get(QuestionBlock.id == 1)
    print(question.text)
    for answer in question.possible_answers:
        print(answer.text)
