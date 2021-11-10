from aiogram.types import Message

from database.models import UserAnswer


class AdminHandler:
    @staticmethod
    async def delete_my_answers(message: Message):
        UserAnswer.delete().where(UserAnswer.user == message.from_user.id).execute()
        await message.answer('Удалил все ваши ответы')
