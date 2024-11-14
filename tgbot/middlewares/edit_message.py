import logging
from typing import Union, Callable, Dict, Awaitable, Any

from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware
from aiogram.types.base import TelegramObject
from aiogram.utils import exceptions


class ReplaceOrDeleteLastMessageMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: Union[types.Update, types.CallbackQuery], data: dict):
        if 'callback_query' in update:
            return
        try:
            last_message_id = int(update.bot["last_message_id"])
            await update.bot.delete_message(chat_id=update.message.chat.id, message_id=last_message_id)
        except KeyError:
            pass
        except exceptions.MessageToDeleteNotFound:
            pass



