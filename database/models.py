import logging

import peewee
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from peewee import Model, TextField, BigIntegerField, ForeignKeyField, DateTimeField

from config import USER_ANSWER_PREFIX
from database.connection import database_connection as db
from attachments.file import Attachment, AttachmentNotSupportedError
from enums.Prefix import CallbackDataPrefix
from datetime import datetime


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    telegram_id = BigIntegerField(primary_key=True)
    first_name = TextField()
    second_name = TextField()
    nick_name = TextField()

    class Meta:
        db_table = 'users'


class PossibleAnswer(BaseModel):
    text = TextField()

    class Meta:
        db_table = 'possible_answers'


class QuestionBlock(BaseModel):
    tour_number = BigIntegerField(primary_key=True)
    file_name = TextField()
    text = TextField()
    right_answer = ForeignKeyField(PossibleAnswer)

    async def edit_sent(self, message: Message,
                        prefix: CallbackDataPrefix,
                        possible_answers: list[PossibleAnswer]):
        try:
            await self.__edit_sent(message, prefix, possible_answers)
        except (AttachmentNotSupportedError, FileNotFoundError) as e:
            logging.error(e)
            await message.answer('Что-то пошло не так, мы уже работаем над ошибкой ...')

    async def __edit_sent(self, message: Message,
                          prefix: CallbackDataPrefix,
                          possible_answers: list[PossibleAnswer]):
        attachment = Attachment.get_attachment_by_file_name(self.file_name)
        input_media = attachment.get_media_file(str(self.text))
        keyboard = self.__get_keyboard(possible_answers, prefix)
        await message.edit_media(input_media, reply_markup=keyboard)

    async def send_to_user(self, message: Message,
                           prefix: CallbackDataPrefix,
                           possible_answers: list[PossibleAnswer]):
        keyboard = self.__get_keyboard(possible_answers, prefix)
        try:
            await self.__send_to_user(message, keyboard)
        except (AttachmentNotSupportedError, FileNotFoundError) as e:
            logging.error(e)
            await message.answer('Что-то пошло не так, мы уже работаем над ошибкой ...')

    def __get_keyboard(self, possible_answers: list[PossibleAnswer], prefix: CallbackDataPrefix):
        keyboard = InlineKeyboardMarkup()
        prefix = prefix.get_full_prefix() + str(self.tour_number) + prefix.split_character
        buttons = [InlineKeyboardButton(text=str(possible_answer.text),
                                        callback_data=prefix + str(possible_answer.id))
                   for possible_answer in possible_answers]
        keyboard.add(*buttons)
        return keyboard

    async def __send_to_user(self, message: Message, reply_markup):
        attachment = Attachment.get_attachment_by_file_name(self.file_name)
        input_file = attachment.get_input_file()
        await attachment.get_answer_method(message)(input_file, caption=self.text, reply_markup=reply_markup)

    @classmethod
    def get_next_question(cls, tour_number) -> 'QuestionBlock':
        next_tour_number = tour_number + 1
        try:
            return cls.get(next_tour_number)
        except peewee.DoesNotExist:
            raise cls.OutOfQuestions('Вопросов больше не осталось!')

    class OutOfQuestions(Exception):
        pass

    class Meta:
        db_table = 'question_blocks'


class Answer(BaseModel):
    user = ForeignKeyField(User)
    question = ForeignKeyField(QuestionBlock)
    answer = ForeignKeyField(PossibleAnswer)
    date = DateTimeField(null=False)

    @classmethod
    def parse(cls, user, callback_data) -> 'Answer':
        split_data = callback_data.split(USER_ANSWER_PREFIX.split_character)
        question_number = int(split_data[0])
        answer_id = split_data[1]
        return cls(user=user,
                   question=question_number,
                   answer=answer_id,
                   date=datetime.utcnow())

    class Meta:
        db_table = 'user_answers'
