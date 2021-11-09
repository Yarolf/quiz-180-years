from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from config import TOKEN

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
