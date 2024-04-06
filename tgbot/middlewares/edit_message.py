from typing import Union

from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware


class ReplaceOrDeleteLastMessageMiddleware(LifetimeControllerMiddleware):
    async def on_pre_process_update(self, update: Union[types.Update, types.CallbackQuery], data: dict):
        print('======================================================')
        if isinstance(update, types.Update):
            message = update.message or update.edited_message
        elif isinstance(update, types.CallbackQuery):
            message = update.message or update.edit_message_text_message

        if message:
            if message.photo or message.text:
                # Если есть фото или текст, заменяем предыдущее сообщение целиком
                last_message_id = data.get('last_message_id')
                if last_message_id:
                    await self.bot.edit_message_media(chat_id=message.chat.id, message_id=last_message_id,
                                                      media=types.InputMediaPhoto(media=message.photo[-1].file_id,
                                                                                 caption=message.caption)
                                                      if message.photo else types.InputMediaText(message.text))
                else:
                    sent_message = await self.bot.send_photo(chat_id=message.chat.id, photo=message.photo[-1].file_id,
                                                             caption=message.caption) if message.photo else \
                        await self.bot.send_message(chat_id=message.chat.id, text=message.text)

                    data['previous_message_id'] = None
                    data['last_message_id'] = sent_message.message_id
            else:
                # Если ни фото, ни текста нет, удаляем предыдущее сообщение
                if data.get('last_message_id'):
                    await self.bot.delete_message(chat_id=message.chat.id, message_id=data['last_message_id'])
                if data.get('previous_message_id'):
                    await self.bot.delete_message(chat_id=message.chat.id, message_id=data['previous_message_id'])

        if isinstance(update, types.CallbackQuery):
            data['previous_message_id'] = data.get('last_message_id')
            data['last_message_id'] = update.message.message_id
        elif message:
            data['previous_message_id'] = data.get('last_message_id')
            data['last_message_id'] = message.message_id
