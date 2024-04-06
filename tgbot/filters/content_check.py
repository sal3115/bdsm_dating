from aiogram.dispatcher.filters import Filter, CommandStart, BoundFilter
from aiogram.types import Message, ContentType


class IsContent(BoundFilter):
    key = 'is_content'
    async def check(self, message: Message):
        if message.content_type == ContentType.PHOTO:
            await message.delete()
            return False
        elif message:
            return True

        else:
            await message.answer('Следуйте инструкции')
            return False
