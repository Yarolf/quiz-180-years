import logging

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from peewee import Model, TextField, BigIntegerField, ForeignKeyField
from database.connection import database_connection as db
from attachments.file import Attachment, AttachmentNotSpecifiedError
from enums.Prefix import CallbackDataPrefix


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

    async def send_to_user(self, message: Message,
                           possible_answers: list[PossibleAnswer],
                           prefix: CallbackDataPrefix):
        keyboard = self.__get_keyboard(possible_answers, prefix)
        try:
            await self.__send_to_user(message, keyboard)
        except AttachmentNotSpecifiedError as e:
            logging.error(e)
            await message.answer('Что-то пошло не так!')

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

    class Meta:
        db_table = 'question_blocks'


class Answer(BaseModel):
    user = ForeignKeyField(User)
    question = ForeignKeyField(QuestionBlock)
    answer = ForeignKeyField(PossibleAnswer)

    class Meta:
        db_table = 'user_answers'
