import logging
from typing import Union, Callable, Dict, Awaitable, Any

from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware
from aiogram.types.base import TelegramObject
from aiogram.utils import exceptions
from aiogram.utils.exceptions import MessageToEditNotFound


# class ReplaceOrDeleteInlineKeyboard(BaseMiddleware):
#     async def on_pre_process_update(self, update: Union[types.Update, types.CallbackQuery], data: dict):
#         if 'callback_query' in update:
#             return
#         try:
#             last_message_id = int(update.bot["last_message_id"])
#             if 'pre_checkout_query' in update:
#                 await update.bot.delete_message( chat_id=update.pre_checkout_query.from_user.id, message_id=last_message_id )
#             else:
#                 await update.bot.delete_message(chat_id=update.message.chat.id, message_id=last_message_id)
#         except KeyError:
#             pass
#         except exceptions.MessageToDeleteNotFound:
#             pass
class ReplaceOrDeleteInlineKeyboard(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.photo: # если есть фото то мы не чего не делаем т.к не срабатывает миделварь с формированием альбома при нескольких фото
            return
        try:
            last_message_id = int(message.bot["last_message_id"])
            logging.info(last_message_id)
            # if 'pre_checkout_query' in message:
            #     await message.bot.delete_message( chat_id=message.pre_checkout_query.from_user.id, message_id=last_message_id )
            # else:
            # await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message_id)
            await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=last_message_id)
        except KeyError:
            pass
        except (exceptions.MessageToDeleteNotFound, MessageToEditNotFound):
            pass
        except exceptions.MessageNotModified:
            pass

# class ReplaceOrDeleteLastMessage(BaseMiddleware):
#     async def on_pre_process_update(self, update: Union[types.Update, types.CallbackQuery], data: dict):
#         if 'pre_checkout_query' in update:
#             return
#         elif 'callback_query' in update:
#             update = update.callback_query
#         try:
#             messages_in_loop = update.bot["messages_in_loop"]
#             if len(messages_in_loop) > 0:
#                 for mess_id in messages_in_loop:
#                     await update.bot.delete_message(chat_id=update.message.chat.id, message_id=mess_id)
#         except KeyError:
#             pass
#         except exceptions.MessageToDeleteNotFound:
#             pass


class ReplaceOrDeleteLastMessage(BaseMiddleware):

    async def on_pre_process_message(self, message: types.Message, data: dict):
        if 'pre_checkout_query' in message:
            return
        try:
            messages_in_loop = message.bot["messages_in_loop"]
            if len(messages_in_loop) > 0:
                for mess_id in messages_in_loop:
                    await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=mess_id)
        except KeyError:
            pass
        except exceptions.MessageToDeleteNotFound:
            pass



class None_last_message(BaseMiddleware):

    async def on_post_process_message(self, message: types.Message, results, data: dict):
        if 'pre_checkout_query' in message:
            return
        try:
            logging.info(f'last_message')
            message.bot["last_message"] = None
        except KeyError:
            pass
    async def on_post_process_callback_query(self, callback_query, results, data: dict):
        if 'pre_checkout_query' in callback_query.message:
            return
        try:
            logging.info(f'last_message')
            callback_query.bot["last_message"] = None
        except KeyError:
            pass
