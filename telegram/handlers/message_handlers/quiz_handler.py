import logging
from aiogram import types
from aiogram.types import CallbackQuery
from database.models import User, QuestionBlock, UserAnswer, PossibleAnswer
from config import USER_ANSWER_PREFIX
from telegram.keyboard import InlineKeyboard
from . import registration_handler


class QuizSender:
    async def send_or_register(self, message: types.Message):
        logging.info(f'{message.from_user.first_name} {message.from_user.last_name} запросил викторину')
        if not User.get_or_none(message.from_user.id):
            await registration_handler.UserRegistrar.process_register_command(message)
            return
        answered_question = UserAnswer.get_last_answered_question_number_or_zero(message.from_user.id)
        await self.__send_not_answered_question_or_refuse(message, answered_question)

    async def __send_not_answered_question_or_refuse(self, message, answered_question):
        try:
            await self.__send_not_answered_question(message, answered_question)
            logging.info(f'отправил викторину {message.from_user.first_name} {message.from_user.last_name}')
        except QuestionBlock.OutOfQuestionsError:
            logging.info(f'{message.from_user.first_name} {message.from_user.last_name} уже проходил викторину')
            await message.answer('Пройти тест можно только один раз!')

    @staticmethod
    async def __send_not_answered_question(message, answered_question):
        question_block = QuestionBlock.get_next_question(answered_question)
        keyboard = InlineKeyboard(USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
        reply_markup = keyboard.get_reply_markup(question_block.tour_number)
        await question_block.send_to_user(message, reply_markup)


class QuizAnswerProcessor:
    async def process_answer_call(self, callback: CallbackQuery):
        try:
            await self.__process_answer_call(callback)
        except QuestionBlock.OutOfQuestionsError:
            await self.__finish_quiz_for_user(callback.message)
            logging.info(f'Завершил викторину для {callback.from_user.first_name} {callback.from_user.last_name}')
        finally:
            await callback.answer()

    @staticmethod
    async def __process_answer_call(callback: CallbackQuery):
        if not User.get_or_none(callback.from_user.id):
            await UserRegistrar.process_register_command(callback.message)
            return
        call_back_data = callback.data.lstrip(USER_ANSWER_PREFIX.get_full_prefix())

        answer = UserAnswer.parse(callback.from_user.id, call_back_data)
        logging.info(f'{callback.from_user.first_name} {callback.from_user.last_name} '
                     f'ответил на {answer.question.tour_number} вопрос')
        last_saved_question_number = UserAnswer.get_last_answered_question_number_or_zero(callback.from_user.id)

        current_question_number = last_saved_question_number
        if answer.question.tour_number > current_question_number:
            current_question_number = answer.question.tour_number
            answer.save()

        question_block = QuestionBlock.get_next_question(current_question_number)
        keyboard = InlineKeyboard(USER_ANSWER_PREFIX, PossibleAnswer.select().execute())
        await question_block.edit_sent(callback.message, keyboard.get_reply_markup(question_block.tour_number))

    @staticmethod
    async def __finish_quiz_for_user(message):
        await message.delete()
        await message.answer('Все ответы приняты, спасибо за участие!')