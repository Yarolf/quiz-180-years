from aiogram.types import Message

from database.models import UserAnswer, User


class AdminHandler:
    @staticmethod
    async def delete_my_answers(message: Message):
        UserAnswer.delete().where(UserAnswer.user == message.from_user.id).execute()
        await message.answer('Удалил все ваши ответы')

    @classmethod
    async def get_winners(cls, message: Message):
        users_answers = UserAnswer.select()
        user_ids = {user_answer.user_id for user_answer in users_answers}
        users_ratings = [UserRating(user_id, get_user_answers(user_id)) for user_id in user_ids]
        sorted_ratings = sorted(users_ratings, key=lambda x: (x.get_rating(), -x.get_elapsed_time()), reverse=True)
        try:
            number_of_winners = int(message.text.split()[1])
        except (IndexError, ValueError):
            await message.answer('Введите команду по шаблону "/get_winners n" , '
                                 'где n (число) - количество победителей, которое вы хотите вывести')
            return
        try:
            for i in range(number_of_winners):
                await message.answer(sorted_ratings[i])
        except IndexError:
            return


def get_user_answers(user_id):
    return UserAnswer.select().where(UserAnswer.user == user_id).order_by(UserAnswer.question)


class UserRating:
    def __init__(self, user_id, answers: list[UserAnswer]):
        self.user_id = user_id
        self.answers = answers

    def __str__(self):
        return str(User.get(self.user_id)) + f"""
        {self.get_rating()=}
        {self.get_elapsed_time()=}
        """

    def get_rating(self):
        count = 0
        for user_answer in self.answers:
            if user_answer.answer == user_answer.question.right_answer:
                count += 1
        return count

    def get_elapsed_time(self):
        return self.answers[-1].date - self.answers[0].date
