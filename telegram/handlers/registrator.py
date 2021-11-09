from aiogram import types

from config import USER_ANSWER_PREFIX
from .error_handlers.error_handler import ErrorHandler
from .message_handlers.base_commands_handler import BaseCommandHandler
from .message_handlers.quiz_handler import QuizSender, QuizAnswerProcessor
from .message_handlers.registration_handler import process_register_command, request_fio
from .message_handlers.registration_handler import process_cancel_command, handle_commands_during_registration
from .message_handlers.registration_handler import register, Registration
from telegram.bot import dispatcher as dp


class HandlerRegistrar:
    def register_all_handlers(self):
        self.register_error_handlers()
        self.register_base_commands_handlers()
        self.register_user_registration_handlers()
        self.register_test_handlers()

    @staticmethod
    def register_error_handlers():
        dp.register_errors_handler(ErrorHandler.handle_error)

    @staticmethod
    def register_base_commands_handlers():
        base_commands_handler = BaseCommandHandler()
        dp.register_message_handler(base_commands_handler.process_start_command, commands=['start'])
        dp.register_message_handler(base_commands_handler.process_help_command, commands=['help'])
        dp.register_message_handler(base_commands_handler.process_about_command, commands=['about'])

    @classmethod
    def register_user_registration_handlers(cls):
        dp.register_message_handler(process_register_command, commands=['register'])
        dp.register_message_handler(request_fio, commands=['update_info'])
        dp.register_message_handler(process_cancel_command, state=Registration.fio, commands=['cancel'])
        dp.register_message_handler(handle_commands_during_registration,
                                    cls.__is_command_except_cancel,
                                    state=Registration.fio)
        dp.register_message_handler(register, state=Registration.fio)

    @staticmethod
    def __is_command_except_cancel(message: types.Message):
        return message.text.startswith('/') and not message.text == '/cancel'

    @staticmethod
    def register_test_handlers():
        quiz_sender = QuizSender()
        quiz_answer_processor = QuizAnswerProcessor()
        dp.register_message_handler(quiz_sender.send_or_register, commands=['test'])
        dp.register_callback_query_handler(quiz_answer_processor.process_answer_call,
                                           lambda call: call.data.startswith(USER_ANSWER_PREFIX.prefix))
