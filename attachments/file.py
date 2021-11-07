import mimetypes
from enum import Enum
import os

from aiogram.types import Message, InputFile, InputMediaPhoto, InputMediaDocument


class FileType(Enum):
    IMAGE = 'image'
    FILE = ''


class File:
    def __init__(self, file_name):
        self.file_path = self.__get_abs_path('files', file_name)

    @staticmethod
    def __get_abs_path(files_folder_name, file_name):
        current_directory = os.path.dirname(__file__)
        return os.path.join(current_directory, files_folder_name, file_name)

    @staticmethod
    def get_answer_method(message: Message):
        return message.answer_document

    def get_input_file(self):
        try:
            return self.__get_input_file()
        except FileNotFoundError:
            raise GetInputFileError(f'Файл {self.file_path} не найден!')

    def __get_input_file(self):
        return InputFile(self.file_path)

    def get_media_file(self, caption):
        try:
            return self._get_media_file(caption)
        except GetInputFileError:
            raise GetMediaFileError(f'Файл {self.file_path} не найден!')

    def _get_media_file(self, caption):
        return InputMediaDocument(self.get_input_file(), caption=caption)


class GetInputFileError(Exception):
    pass


class GetMediaFileError(GetInputFileError):
    pass


class Image(File):
    def _get_media_file(self, caption):
        return InputMediaPhoto(self.get_input_file(), caption=caption)

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
        except UnknownFileTypeError:
            raise AttachmentNotSupportedError(f'Такой тип файла не поддерживается: {file_name}')

    @classmethod
    def __get_attachment_by_file_name(cls, file_name):
        file_type = cls.__get_file_type(mimetypes.guess_type(file_name))
        attachment_class = cls.__possible_attachments[file_type]
        return attachment_class(file_name)

    @classmethod
    def __get_file_type(cls, mimetype):
        """mimetype - кортеж (type, encoding), где type - это строка, вида: type/subtype"""
        type_subtype = mimetype[0]
        if not type_subtype:
            raise UnknownFileTypeError('Неизвестный тип файла!')
        return type_subtype.split('/')[0]


class UnknownFileTypeError(Exception):
    pass


class AttachmentNotSupportedError(Exception):
    pass
