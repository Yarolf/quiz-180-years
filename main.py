import logging
import os
from telegram.bot import bot, dispatcher as dp
import config
from aiogram.utils.executor import start_webhook, start_polling
from database.models import User, UserAnswer, QuestionBlock, PossibleAnswer
from database.connection import database_connection as db

from telegram.handlers.registrator import register_all_handlers


async def on_startup(dispatcher):
    await bot.set_webhook(config.WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


def prepare():
    logging.basicConfig(level=logging.INFO)
    register_all_handlers()
    with db:
        db.create_tables([User, UserAnswer, QuestionBlock, PossibleAnswer])


if __name__ == '__main__':
    prepare()
    if os.getenv('HEROKU'):
        print('!!! USING WEBHOOK NOW !!!!')
        start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=config.WEBAPP_HOST,
            port=config.WEBAPP_PORT,
        )
    else:
        print('!!!!USING LONG POLLING NOW!!!!')
        start_polling(dp, skip_updates=True)
