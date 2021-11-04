from peewee import Model, TextField, BigIntegerField
from database.connection import database_connection as db


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    first_name = TextField()
    second_name = TextField()
    nick_name = TextField()
    telegram_id = BigIntegerField()

    class Meta:
        db_table = 'users'
