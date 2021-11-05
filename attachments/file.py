import mimetypes
from enum import Enum
import os

from aiogram.types import InputFile, InputMediaPhoto


class FileType(Enum):
    IMAGE = 'image'


class File:
    def __init__(self, file_name):
        self.file_path = self.__get_abs_path(file_name)

    @staticmethod
    def __get_abs_path(file_name):
        current_direction = os.path.dirname(__file__)
        return os.path.join(current_direction, file_name)

    def get_input_file(self):
        return InputFile(self.file_path)


class Image(File):
    def get_input_file(self):
        return InputMediaPhoto(self.file_path)


class Attachment:
    __possible_attachments = {
        FileType.IMAGE.value: Image
    }

    @classmethod
    def get_attachment_by_file_name(cls, file_name):
        try:
            return cls.__get_attachment_by_file_name(file_name)
        except KeyError:
            raise AttachmentNotSpecifiedError('Такой тип файла не поддерживается!')

    @classmethod
    def __get_attachment_by_file_name(cls, file_name):
        # кортеж (type, encoding), где type - это строка, вида: type/subtype
        file_type = mimetypes.guess_type(file_name)[0].split('/')[0]
        attachment_class = cls.__possible_attachments[file_type]
        return attachment_class(file_name)


class AttachmentNotSpecifiedError(Exception):
    pass
