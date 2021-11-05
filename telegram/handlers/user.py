from aiogram import types
from aiogram.types import CallbackQuery

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock, Answer, PossibleAnswer
from config import USER_ANSWER_PREFIX


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
    question_block: QuestionBlock = QuestionBlock.get(1)
    await question_block.send_to_user(message, USER_ANSWER_PREFIX, PossibleAnswer.select().execute())


@dp.callback_query_handler(lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
async def process_answer_call(call_back: CallbackQuery):
    await call_back.message.delete()
    call_back_data = call_back.data.lstrip(USER_ANSWER_PREFIX.get_full_prefix())
    answer = Answer.parse(call_back.from_user.id, call_back_data)
    answer.save()

    question_block: QuestionBlock = QuestionBlock.try_get_next_question(answer.question.tour_number)
    if question_block is not None:
        await question_block.send_to_user(call_back.message, USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
    else:
        await call_back.message.answer('Спасибо за участие!')
    await call_back.answer()



