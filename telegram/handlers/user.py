from aiogram import types
from aiogram.types import CallbackQuery

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock, UserAnswer, PossibleAnswer
from config import USER_ANSWER_PREFIX
import peewee


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'Пользователь {message.from_user.first_name} {message.from_user.last_name} ввёл команду start')
    await process_register_command(message)
    await process_test_command(message)


@dp.message_handler(commands=['register'])
async def process_register_command(message: types.Message):
    try:
        User.get_or_create(telegram_id=message.from_user.id,
                           first_name=message.from_user.first_name,
                           second_name=message.from_user.last_name,
                           nick_name=message.from_user.username)
    except peewee.IntegrityError:
        User.update(first_name=message.from_user.first_name,
                    second_name=message.from_user.last_name,
                    nick_name=message.from_user.username).\
            where(User.telegram_id == message.from_user.id).\
            execute()


@dp.message_handler(commands=['test'])
async def process_test_command(message: types.Message):
    try:
        answered_question = UserAnswer.get_last_answered(message.from_user.id).question.tour_number
    except IndexError:
        answered_question = 0
    try:
        question_block: QuestionBlock = QuestionBlock.get_next_question(answered_question)
        await question_block.send_to_user(message, USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
    except QuestionBlock.OutOfQuestions:
        await message.answer('Пройти тест можно только один раз!')


@dp.callback_query_handler(lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
async def process_answer_call(callback: CallbackQuery):
    try:
        await __process_answer_call(callback)
    except QuestionBlock.OutOfQuestions:
        await callback.message.delete()
        await callback.message.answer('Все ответы приняты, спасибо за участие!')
    finally:
        await callback.answer()


async def __process_answer_call(callback: CallbackQuery):
    call_back_data = callback.data.lstrip(USER_ANSWER_PREFIX.get_full_prefix())
    answer = UserAnswer.parse(callback.from_user.id, call_back_data)
    try:
        answered_question = UserAnswer.get_last_answered(callback.from_user.id).question.tour_number
    except IndexError:
        answered_question = 0
    if answer.question.tour_number <= answered_question:
        question_block = QuestionBlock.get_next_question(answered_question)
    else:
        answer.save()
        question_block = QuestionBlock.get_next_question(answer.question.tour_number)
    await question_block.edit_sent(callback.message, USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
