import logging

import peewee
from aiogram.types import Message, InlineKeyboardMarkup
from peewee import Model, TextField, BigIntegerField, ForeignKeyField, DateTimeField

from config import USER_ANSWER_PREFIX
from database.connection import database_connection as db
from attachments.file import Attachment, GetInputFileError, GetMediaFileError, AttachmentNotSupportedError
from datetime import datetime


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    telegram_id = BigIntegerField(primary_key=True)
    first_name = TextField()
    second_name = TextField(null=True)
    nick_name = TextField(null=True)

    @classmethod
    def register_or_update(cls, telegram_id, first_name, second_name, nick_name):
        try:
            User.register(telegram_id=telegram_id,
                          first_name=first_name,
                          second_name=second_name,
                          nick_name=nick_name)
        except cls.UserAlreadyExistsError:
            User.update(first_name=first_name,
                        second_name=second_name,
                        nick_name=nick_name). \
                where(User.telegram_id == telegram_id). \
                execute()

    @classmethod
    def register(cls, telegram_id, first_name, second_name, nick_name):
        if cls.get_or_none(telegram_id):
            raise cls.UserAlreadyExistsError('Пользователь уже существует!')

        cls.create(telegram_id=telegram_id,
                   first_name=first_name,
                   second_name=second_name,
                   nick_name=nick_name)

    class UserAlreadyExistsError(Exception):
        pass

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

    async def send_to_user(self, message: Message,
                           reply_markup: InlineKeyboardMarkup):
        try:
            await self.__send_to_user(message, reply_markup)
        except (AttachmentNotSupportedError, GetInputFileError) as e:
            logging.error(e)
            await message.answer('Что-то пошло не так, мы уже работаем над ошибкой ...')

    async def __send_to_user(self, message: Message, reply_markup):
        attachment = Attachment.get_attachment_by_file_name(self.file_name)
        input_file = attachment.get_input_file()
        await attachment.get_answer_method(message)(input_file, caption=self.text, reply_markup=reply_markup)

    async def edit_sent(self, message: Message,
                        reply_markup: InlineKeyboardMarkup):
        try:
            await self.__edit_sent(message, reply_markup)
        except (AttachmentNotSupportedError, GetMediaFileError) as e:
            logging.error(e)
            await message.answer('Что-то пошло не так, мы уже работаем над ошибкой ...')

    async def __edit_sent(self, message: Message,
                          reply_markup: InlineKeyboardMarkup):
        attachment = Attachment.get_attachment_by_file_name(self.file_name)
        input_media = attachment.get_media_file(self.text)
        await message.edit_media(input_media, reply_markup=reply_markup)

    @classmethod
    def get_next_question(cls, tour_number) -> 'QuestionBlock':
        next_tour_number = tour_number + 1
        try:
            return cls.get(next_tour_number)
        except peewee.DoesNotExist:
            raise cls.OutOfQuestionsError('Вопросов больше не осталось!')

    class OutOfQuestionsError(Exception):
        pass

    class Meta:
        db_table = 'question_blocks'


class UserAnswer(BaseModel):
    user: User = ForeignKeyField(User)
    question: QuestionBlock = ForeignKeyField(QuestionBlock)
    answer: PossibleAnswer = ForeignKeyField(PossibleAnswer)
    date: datetime = DateTimeField(null=False)

    @classmethod
    def parse(cls, user, callback_data) -> 'UserAnswer':
        split_data = callback_data.split(USER_ANSWER_PREFIX.split_character)
        question_number = int(split_data[0])
        answer_id = split_data[1]
        return cls(user=user,
                   question=question_number,
                   answer=answer_id,
                   date=datetime.utcnow())

    @classmethod
    def try_get_last_answered_question_number(cls, user_id) -> BigIntegerField or int:
        """ Возвращает наибольший номер вопроса, на который ответил пользователь
        или 0, если ответов от пользователя не найдено"""
        try:
            return cls.get_last_answered(user_id).question.tour_number
        except IndexError:
            return 0

    @classmethod
    def get_last_answered(cls, user_id) -> 'UserAnswer':
        query: list[cls] = cls.select(). \
            where(cls.user == user_id). \
            order_by(cls.question.desc()). \
            limit(1)
        return query[0]

    class Meta:
        db_table = 'user_answers'
