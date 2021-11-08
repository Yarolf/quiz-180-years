from aiogram import types
from aiogram.types import CallbackQuery

from telegram.bot import dispatcher as dp
import logging
from database.models import User, QuestionBlock, UserAnswer, PossibleAnswer
from config import USER_ANSWER_PREFIX
from telegram.keyboard import InlineKeyboard


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logging.info(f'{message.from_user.first_name} {message.from_user.last_name} ввёл команду start')
    await process_register_command(message)


@dp.message_handler(commands=['about'])
async def send_about(message: types.Message):
    await message.answer('Добрый день! Это бот для прохождения викторины, посвященной 180 летию Сбера!')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer("""
    Список доступных команд:
    /about - информация о боте
    /register - зарегистрироваться
    /update_info - обновить данных профиля
    /test - пройти тест""")


@dp.message_handler(commands=['register'])
async def process_register_command(message: types.Message):
    await message.answer('Добрый день! Перед началом викторины приглашаем пройти регистрацию.')
    await request_contact(message)


@dp.message_handler(commands=['update_info'])
async def request_contact(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='Предоставить телефон', request_contact=True))
    logging.info(f'Запросил контакт у {message.from_user.first_name} {message.from_user.last_name}')
    await message.answer('Для того, чтобы мы смогли связаться с вами в случае победы, '
                         'предоставьте, пожалуйста, свои контактные данные, '
                         'нажав на кнопку ниже.', reply_markup=keyboard)


@dp.message_handler(content_types=['contact'])
async def register(message: types.Message):
    logging.info(f'Получил контакт от {message.from_user.first_name} {message.from_user.last_name}')
    User.register_or_update(message.from_user.id,
                            message.from_user.first_name,
                            message.from_user.last_name,
                            message.from_user.username,
                            message.contact.phone_number)
    logging.info(f'Зарегистрировал {message.from_user.first_name} {message.from_user.last_name}')
    await message.answer('Регистрация прошла успешно!', reply_markup=types.ReplyKeyboardRemove())
    await message.answer('Для прохождения теста введите команду  /test')


@dp.message_handler(commands=['test'])
async def process_test_command(message: types.Message):
    logging.info(f'{message.from_user.first_name} {message.from_user.last_name} ввёл команду test')
    if not User.get_or_none(message.from_user.id):
        await process_register_command(message)
        return
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
    if not User.get_or_none(callback.from_user.id):
        await process_register_command(callback.message)
        return
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
