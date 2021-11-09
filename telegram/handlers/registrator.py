from aiogram import types

from config import USER_ANSWER_PREFIX
from .error_handlers.error_handler import handle_error
from .message_handlers.base_commands_handler import process_start_command, process_help_command, process_about_command
from .message_handlers.quiz_handler import process_test_command, process_answer_call
from .message_handlers.registration_handler import process_register_command, request_fio, process_cancel_command, \
    handle_commands_during_registration, register, Registration

from telegram.bot import dispatcher as dp


def register_all_handlers():
    register_error_handlers()
    register_base_commands_handlers()
    register_user_registration_handlers()
    register_test_handlers()


def register_error_handlers():
    dp.register_errors_handler(handle_error)


def register_base_commands_handlers():
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(process_help_command, commands=['help'])
    dp.register_message_handler(process_about_command, commands=['about'])


def register_user_registration_handlers():
    dp.register_message_handler(process_register_command, commands=['register'])
    dp.register_message_handler(request_fio, commands=['update_info'])
    dp.register_message_handler(process_cancel_command, state=Registration.fio, commands=['cancel'])
    dp.register_message_handler(handle_commands_during_registration,
                                __all_commands_except_cancel,
                                state=Registration.fio)
    dp.register_message_handler(register, state=Registration.fio)


def __all_commands_except_cancel(message: types.Message):
    return message.text.startswith('/') and not message.text == '/cancel'


def register_test_handlers():
    dp.register_message_handler(process_test_command, commands=['test'])
    dp.register_callback_query_handler(process_answer_call,
                                       lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
