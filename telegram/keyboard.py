from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.models import PossibleAnswer
from enums.Prefix import CallbackDataPrefix


class InlineKeyboard:
    def __init__(self, possible_answers: list[PossibleAnswer], prefix: CallbackDataPrefix):
        self.possible_answers = possible_answers
        self.prefix = prefix

    def get_reply_markup(self, tour_number) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        prefix = self.prefix.get_full_prefix() + str(tour_number) + self.prefix.split_character
        buttons = [InlineKeyboardButton(text=str(possible_answer.text),
                                        callback_data=prefix + str(possible_answer.id))
                   for possible_answer in self.possible_answers]
        keyboard.add(*buttons)
        return keyboard
