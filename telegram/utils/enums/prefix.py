from enum import Enum


class Prefix(Enum):
    USER_ANSWER = 'usans'


class SplitCharacter(Enum):
    FORWARD_SLASH = '|'


class CallbackDataPrefix:
    def __init__(self, prefix, split_character):
        self.prefix: str = prefix
        self.split_character: str = split_character

    def get_full_prefix(self):
        return self.prefix + self.split_character

