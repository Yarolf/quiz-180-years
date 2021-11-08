from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import PossibleAnswer
from telegram.utils.callback_data import CallbackAnswerData
from telegram.utils.enums.prefix import CallbackDataPrefix


class InlineKeyboard:
    def __init__(self, prefix: CallbackDataPrefix, possible_answers: list[PossibleAnswer]):
        self.possible_answers = possible_answers
        self.prefix = prefix

    def get_reply_markup(self, question_number) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        buttons = [InlineKeyboardButton(text=str(possible_answer.text),
                                        callback_data=CallbackAnswerData(prefix=self.prefix,
                                                                         question_number=question_number,
                                                                         answer_id=possible_answer.id).get_full())
                   for possible_answer in self.possible_answers]
        keyboard.add(*buttons)
        return keyboard
