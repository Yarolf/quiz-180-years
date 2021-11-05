from peewee import Model, TextField, BigIntegerField, ForeignKeyField
from database.connection import database_connection as db


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

    class Meta:
        db_table = 'question_blocks'
