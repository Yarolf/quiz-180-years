from peewee import Model, TextField, BigIntegerField
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
