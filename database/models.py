import logging

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from peewee import Model, TextField, BigIntegerField, ForeignKeyField
from database.connection import database_connection as db
from attachments.file import Attachment, AttachmentNotSpecifiedError


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


class Answer(BaseModel):
    user = ForeignKeyField(User)
    answer = TextField()

    class Meta:
        db_table = 'user_answers'


class PossibleAnswer(BaseModel):
    text = TextField()

    class Meta:
        db_table = 'possible_answers'


class QuestionBlock(BaseModel):
    file_name = TextField()
    text = TextField()
    right_answer = ForeignKeyField(PossibleAnswer)

    async def send_to_user(self, message: Message, possible_answers: list[PossibleAnswer]):
        try:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(*[InlineKeyboardButton(text=str(possible_answer.text), callback_data=possible_answer.id)
                           for possible_answer in possible_answers])
            await self.__send_to_user(message, keyboard)
        except AttachmentNotSpecifiedError as e:
            logging.error(e)
            await message.answer('Что-то пошло не так!')

    async def __send_to_user(self, message: Message, reply_markup):
        attachment = Attachment.get_attachment_by_file_name(self.file_name)
        input_file = attachment.get_input_file()
        await attachment.get_answer_method(message)(input_file, caption=self.text, reply_markup=reply_markup)

    class Meta:
        db_table = 'question_blocks'
