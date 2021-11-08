from telegram.utils.enums.prefix import CallbackDataPrefix


class CallbackData:
    def __init__(self, prefix: CallbackDataPrefix):
        self.prefix = prefix

    def get_full(self):
        return self.prefix.get_full_prefix()


class CallbackAnswerData(CallbackData):
    def __init__(self, prefix: CallbackDataPrefix, question_number, answer_id):
        CallbackData.__init__(self, prefix)
        self.question_number = question_number
        self.answer_id = answer_id

    def get_full(self):
        prefix = super(CallbackAnswerData, self).get_full()
        data = [self.question_number, self.answer_id]
        return prefix + self.prefix.split_character.join(map(str, data))

    @classmethod
    def parse(cls, prefix: CallbackDataPrefix, callback_data: str):
        split_data = callback_data.split(prefix.split_character)
        question_number = int(split_data[0])
        answer_id = split_data[1]
        return cls(prefix, question_number, answer_id)



