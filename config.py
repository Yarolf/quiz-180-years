import os

from telegram.utils.enums.prefix import CallbackDataPrefix, Prefix, SplitCharacter

TOKEN = os.getenv('BOT_TOKEN')

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

DB_URL = os.getenv('DATABASE_URL')

USER_ANSWER_PREFIX = CallbackDataPrefix(Prefix.USER_ANSWER.value, SplitCharacter.FORWARD_SLASH.value)
