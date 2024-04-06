import datetime
import logging

from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tgbot.models.sql_request import select_user, update_user_info, update_active_day


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        db_session = obj.bot.get('session_maker')
        today = datetime.datetime.today().date()
        if isinstance(obj, types.Message):
            user_id = obj.chat.id
        elif isinstance(obj, types.CallbackQuery):
            user_id = obj.message.chat.id
        else:
            return
        user_info = await select_user(session=db_session, user_id=user_id)
        if len(user_info)==0:
            return
        last_date_user = user_info[0]['last_time']
        if last_date_user != today:
            await update_user_info(session=db_session, user_id=user_id, last_time = today)
            await update_active_day(session=db_session, user_id=user_id)


        # Передаем данные из таблицы в хендлер
        # data['some_model'] = await Model.get()
