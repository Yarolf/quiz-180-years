from aiogram import types
from aiogram.types import CallbackQuery

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock, PossibleAnswer
from attachments.file import AttachmentNotSpecifiedError
from config import USER_ANSWER_PREFIX


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'Пользователь {message.from_user.id} ввёл команду start')
    User.get_or_create(telegram_id=message.from_user.id,
                       first_name=message.from_user.first_name,
                       second_name=message.from_user.last_name,
                       nick_name=message.from_user.username)
    await process_test_command(message)


@dp.message_handler(commands=['test'])
async def process_test_command(message: types.Message):
    question: QuestionBlock = QuestionBlock.get(QuestionBlock.id == 1)
    try:
        possible_answers = PossibleAnswer.select().execute()
        await question.send_to_user(message, possible_answers, USER_ANSWER_PREFIX)
    except AttachmentNotSpecifiedError:
        await message.answer('Что-то пошло не так(')
        logging.info(f'Тип файла не поддерживается: {question.file_name}')


@dp.callback_query_handler(lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
async def process_answer_call(call_back: CallbackQuery):
    try:
        await call_back.message.delete()
        call_back_data = call_back.data.lstrip(USER_ANSWER_PREFIX.get_full_prefix())
        tour_number = int(call_back_data.split(USER_ANSWER_PREFIX.split_character)[0]) + 1
        print(tour_number)
        question: QuestionBlock = QuestionBlock.get(QuestionBlock.tour_number == tour_number)
        try:
            possible_answers = PossibleAnswer.select().execute()
            await question.send_to_user(call_back.message, possible_answers, USER_ANSWER_PREFIX)
        except AttachmentNotSpecifiedError:
            await call_back.message.answer('Что-то пошло не так(')
            logging.info(f'Тип файла не поддерживается: {question.file_name}')
    except Exception:
        await call_back.message.answer('Спасибо за участие!')

