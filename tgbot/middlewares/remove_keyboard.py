import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware


class RemoveInlineKeyboardMiddleware( BaseMiddleware ):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logging.info( ["data.get( 'last_message_id' )", data.get( 'last_message_id' )] )
        try:
            data['previous_message_id'] = data['last_message_id']
        except KeyError:
            data['previous_message_id'] = None

        data['last_message_id'] = message.message_id
        logging.info(['data', data, type(data)])
    async def on_post_process_message(self, message: types.Message, data: dict, *args):
        logging.info(['data', data, type(data)])
        logging.info(["data['previous_message_id']"], data)
        data['previous_message_id'] = data.get( 'last_message_id', None )
