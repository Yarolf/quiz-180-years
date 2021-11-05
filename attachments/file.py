import mimetypes
from enum import Enum
import os

from aiogram.types import InputFile, InputMediaPhoto, Message


class FileType(Enum):
    IMAGE = 'image'


class File:
    def __init__(self, file_name):
        self.file_path = self.__get_abs_path(file_name)

    @staticmethod
    def __get_abs_path(file_name):
        current_direction = os.path.dirname(__file__)
        files_folder_name = 'files'
        return os.path.join(current_direction, files_folder_name, file_name)

    def get_input_file(self):
        return InputFile(self.file_path)

    @staticmethod
    def get_answer_method(message: Message):
        return message.answer_document


class Image(File):
    def get_input_file(self):
        return InputFile(self.file_path)

    @staticmethod
    def get_answer_method(message: Message):
        return message.answer_photo


class Attachment:
    __possible_attachments = {
        FileType.IMAGE.value: Image
    }

    @classmethod
    def get_attachment_by_file_name(cls, file_name):
        try:
            return cls.__get_attachment_by_file_name(file_name)
        except AttachmentNotSpecifiedError:
            raise AttachmentNotSpecifiedError(f'Такой тип файла не поддерживается: {file_name}')

    @classmethod
    def __get_attachment_by_file_name(cls, file_name):
        file_type = cls.__get_file_type(mimetypes.guess_type(file_name))
        attachment_class = cls.__possible_attachments[file_type]
        return attachment_class(file_name)

    @staticmethod
    def __get_file_type(mimetype):
        """mimetype - кортеж (type, encoding), где type - это строка, вида: type/subtype"""
        type_subtype = mimetype[0]
        if not type_subtype:
            raise AttachmentNotSpecifiedError('Неизвестный тип файла!')
        return type_subtype.split('/')[0]


class AttachmentNotSpecifiedError(Exception):
    pass
