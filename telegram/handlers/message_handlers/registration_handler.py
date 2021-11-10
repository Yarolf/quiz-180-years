import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from database.models import User
from . import quiz_handler


class Registration(StatesGroup):
    fio = State()


class UserRegistrar:
    @classmethod
    async def process_register_command(cls, message: types.Message):
        await message.answer('Добрый день! Перед началом викторины приглашаем пройти регистрацию.')
        await cls.request_fio(message)

    @staticmethod
    async def request_fio(message: types.Message):
        logging.info(f'Запросил фио {message.from_user.first_name} {message.from_user.last_name}')
        await message.answer('Пожалуйста, отправьте свои фамилию имя и отчество одним сообщением:')
        await Registration.fio.set()

    @staticmethod
    async def process_cancel_command(message: types.Message, state: FSMContext):
        await state.finish()
        logging.info(f'{message.from_user.first_name} {message.from_user.last_name} отменил регистрацию')
        await message.answer('Регистрация отменена!')

    @staticmethod
    async def handle_commands_during_registration(message: types.Message):
        logging.info(f'{message.from_user.first_name} {message.from_user.last_name} вместо фио ввёл команду {message.text}')
        await message.answer('Необходимо ввести фамилию имя и отчество, для отмены введите  /cancel')

    @staticmethod
    async def register(message: types.Message, state: FSMContext):
        logging.info(f'Получил фио от {message.from_user.first_name} {message.from_user.last_name}')
        User.register_or_update(message.from_user.id,
                                message.from_user.first_name,
                                message.from_user.last_name,
                                message.from_user.username,
                                message.text
                                )
        await state.finish()
        logging.info(f'Зарегистрировал {message.from_user.first_name} {message.from_user.last_name} как {message.text}')
        await message.answer('Регистрация прошла успешно!', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Запускаю викторину:')
        quiz_sender = quiz_handler.QuizSender()
        await quiz_sender.send_or_register(message)
