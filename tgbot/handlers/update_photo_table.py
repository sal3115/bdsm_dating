import logging
from typing import Union

from aiogram import types
from sqlalchemy import select, update

from tgbot.models.Users import PhotoTable


async def db_photos_table(session):
    request = select( PhotoTable.photo_id)
    with session() as ses:
        with ses.begin():
            answer = ses.execute( request )
            answer2 = [dict( r._mapping ) for r in answer.fetchall()]
            return answer2

async def update_photo_func(message: Union[types.Message, types.CallbackQuery]):
    session = message.bot.data['session_maker']
    photo_ids = await db_photos_table(session=session)
    for photo_id in photo_ids:
        logging.info(f'------------photo_id--------------{photo_id["photo_id"]}')
        # Отправляем фото в чат
        photo_url = photo_id["photo_id"]
        message = await message.bot.send_photo(chat_id='1790645630', photo=photo_url)

        # Получаем unique_id
        unique_id = message.photo[-1].file_unique_id

        # Обновляем данные в таблице
        # photo = session.query(PhotoTable).filter_by(photo_id=photo_id).first()
        # photo.unique_id = unique_id
        stmt = update( PhotoTable ).where(PhotoTable.photo_id==photo_url).values(unique_id=unique_id)
        with session() as ses:
            with ses.begin():
                ses.execute( stmt )
        await message.delete()