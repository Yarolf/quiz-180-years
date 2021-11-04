from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from config import TOKEN

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot)

# disabling other loggers
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
