from peewee import Model, TextField, BigIntegerField, ForeignKeyField
from database.connection import database_connection as db
from playhouse.postgres_ext import ArrayField


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


class QuestionBlock(BaseModel):
    file_path = TextField()
    text = TextField()
    possible_answers = ArrayField(TextField, default=['ДА', 'НЕТ'])

    class Meta:
        db_table = 'question_blocks'

