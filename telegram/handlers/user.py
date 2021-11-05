from aiogram import types
from aiogram.types import CallbackQuery

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock, PossibleAnswer, Answer
from attachments.file import AttachmentNotSpecifiedError
from config import USER_ANSWER_PREFIX
import peewee


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'Пользователь {message.from_user.first_name} {message.from_user.last_name} ввёл команду start')
    User.get_or_create(telegram_id=message.from_user.id,
                       first_name=message.from_user.first_name,
                       second_name=message.from_user.last_name,
                       nick_name=message.from_user.username)
    await process_test_command(message)


@dp.message_handler(commands=['test'])
async def process_test_command(message: types.Message):
    question: QuestionBlock = QuestionBlock.get(QuestionBlock.tour_number == 1)
    try:
        possible_answers = PossibleAnswer.select().execute()
        await question.send_to_user(message, possible_answers, USER_ANSWER_PREFIX)
    except AttachmentNotSpecifiedError:
        await message.answer('Что-то пошло не так(')
        logging.info(f'Тип файла не поддерживается: {question.file_name}')


@dp.callback_query_handler(lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
async def process_answer_call(call_back: CallbackQuery):
    await call_back.message.delete()
    call_back_data = call_back.data.lstrip(USER_ANSWER_PREFIX.get_full_prefix())
    split_data = call_back_data.split(USER_ANSWER_PREFIX.split_character)
    tour_number = int(split_data[0])
    answer_id = split_data[1]
    Answer.insert(user=call_back.from_user.id, answer=answer_id).execute()

    try:
        question = get_next_tour(tour_number)
    except OutOfTours:
        await call_back.message.answer('Спасибо за участие!')
        await call_back.answer()
        return

    try:
        possible_answers = PossibleAnswer.select().execute()
        await question.send_to_user(call_back.message, possible_answers, USER_ANSWER_PREFIX)
    except AttachmentNotSpecifiedError:
        await call_back.message.answer('Что-то пошло не так(')
        logging.info(f'Тип файла не поддерживается: {question.file_name}')
    await call_back.answer()


def get_next_tour(tour_number):
    next_tour_number = tour_number + 1
    try:
        return QuestionBlock.get(QuestionBlock.tour_number == next_tour_number)
    except peewee.DoesNotExist:
        raise OutOfTours('Туров больше не осталось!')


class OutOfTours(Exception):
    pass

