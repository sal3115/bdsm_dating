from aiogram.dispatcher.filters import BoundFilter

from aiogram.types import Message

from tgbot.services.anketa_utulites import check_name


class KirilitsaFilter(BoundFilter):  # [1]
    async def check(self, message: Message):
        return await check_name(message.text)