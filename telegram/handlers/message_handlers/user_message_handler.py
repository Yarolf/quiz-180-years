from aiogram import types
from aiogram.types import CallbackQuery

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock, UserAnswer, PossibleAnswer
from config import USER_ANSWER_PREFIX
from telegram.keyboard import InlineKeyboard


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'Пользователь {message.from_user.first_name} {message.from_user.last_name} ввёл команду start')
    await process_register_command(message)
    await process_test_command(message)


@dp.message_handler(commands=['register'])
async def process_register_command(message: types.Message):
    User.register_or_update(message.from_user.id,
                            message.from_user.first_name,
                            message.from_user.last_name,
                            message.from_user.username)


@dp.message_handler(commands=['give_contact'])
async def request_contact(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Предоставить телефон', request_contact=True))
    await message.answer('Нажмите на кнопку для отправки вашего контакта.', reply_markup=keyboard)


@dp.message_handler(content_types=['contact'])
async def get_contact(message: types.Message):
    await message.answer(message.contact.phone_number, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['test'])
async def process_test_command(message: types.Message):
    answered_question = UserAnswer.get_last_answered_question_number_or_zero(message.from_user.id)
    await send_next_question(message, answered_question)


async def send_next_question(message, answered_question):
    try:
        await __send_next_question(message, answered_question)
    except QuestionBlock.OutOfQuestionsError:
        await message.answer('Пройти тест можно только один раз!')


async def __send_next_question(message, answered_question):
    question_block = QuestionBlock.get_next_question(answered_question)
    keyboard = InlineKeyboard(USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
    reply_markup = keyboard.get_reply_markup(question_block.tour_number)
    await question_block.send_to_user(message, reply_markup)


@dp.callback_query_handler(lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
async def process_answer_call(callback: CallbackQuery):
    try:
        await __process_answer_call(callback)
    except QuestionBlock.OutOfQuestionsError:
        await __finish_quiz_for_user(callback.message)
    finally:
        await callback.answer()


async def __process_answer_call(callback: CallbackQuery):
    call_back_data = callback.data.lstrip(USER_ANSWER_PREFIX.get_full_prefix())

    answer = UserAnswer.parse(callback.from_user.id, call_back_data)
    last_saved_question_number = UserAnswer.get_last_answered_question_number_or_zero(callback.from_user.id)

    current_question_number = last_saved_question_number
    if answer.question.tour_number > current_question_number:
        current_question_number = answer.question.tour_number
        answer.save()

    question_block = QuestionBlock.get_next_question(current_question_number)
    keyboard = InlineKeyboard(USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
    await question_block.edit_sent(callback.message, keyboard.get_reply_markup(question_block.tour_number))


async def __finish_quiz_for_user(message):
    await message.delete()
    await message.answer('Все ответы приняты, спасибо за участие!')
