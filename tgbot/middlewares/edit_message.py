import logging
from typing import Union, Callable, Dict, Awaitable, Any

from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware
from aiogram.types.base import TelegramObject
from aiogram.utils import exceptions


class ReplaceOrDeleteInlineKeyboard(BaseMiddleware):
    async def on_pre_process_update(self, update: Union[types.Update, types.CallbackQuery], data: dict):
        if 'callback_query' in update:
            return
        try:
            logging.info(update)
            last_message_id = int(update.bot["last_message_id"])
            if 'pre_checkout_query' in update:
                await update.bot.delete_message( chat_id=update.pre_checkout_query.from_user.id, message_id=last_message_id )
            else:
                await update.bot.delete_message(chat_id=update.message.chat.id, message_id=last_message_id)
        except KeyError:
            pass
        except exceptions.MessageToDeleteNotFound:
            pass


class ReplaceOrDeleteLastMessage(BaseMiddleware):
    async def on_pre_process_update(self, update: Union[types.Update, types.CallbackQuery], data: dict):
        if 'pre_checkout_query' in update:
            return
        elif 'callback_query' in update:
            update = update.callback_query
        try:
            logging.info(update)
            messages_in_loop = update.bot["messages_in_loop"]
            if len(messages_in_loop) > 0:
                for mess_id in messages_in_loop:
                    await update.bot.delete_message(chat_id=update.message.chat.id, message_id=mess_id)
        except KeyError:
            pass
        except exceptions.MessageToDeleteNotFound:
            pass


