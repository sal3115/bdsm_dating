import asyncio
import logging
import textwrap
from math import ceil

from tgbot.models.engine import create_engine_db, get_session_maker
from tgbot.models.sql_request import insert_users

users = {'user_id':465090182, 'name': "asasa",  'user_name':  "salvat3115",   'gender': "women" ,
         'birthday': "2001-01-01" ,  'city': "фывфы" , 'about_me':  "фывфыв", 'partner_another_city':False,
         'min_age':18, 'max_age':23, 'practice': 'Оарарфыраы', 'tabu': 'asdadasdasdas'}
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     engine = create_engine_db( db_path='localhost', db_user='user_bdsm', db_pass='78O89p96', name_db='db_bdsm'  )
#
#     session = get_session_maker( engine )
#     for k in range(10):
#         users['user_id'] = users['user_id'] + k+1
#         print(users['user_id'] )
#         lll = loop.run_until_complete( insert_users( session=session, params = users ) )
async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    if photo:  # если есть фото, изменяем сообщение с фото
        media = InputMedia(media=photo)
        if message.photo:
            try:
                await message.edit_media( media=media )
                message_callback = await message.edit_caption( caption=text, reply_markup=markup)
            except MessageCantBeEdited:
                message_callback = await message.answer_photo(photo=photo, caption=text, reply_markup=markup)
            except BadRequest:
                message_callback = await message.answer_photo( photo=photo, caption=text, reply_markup=markup )
        else:
            await message.delete()
            message_callback = await message.answer_photo(photo=photo,caption=text, reply_markup=markup)
    elif video:
        # если есть видео, изменяем сообщение с видео
        # await message.edit_caption( caption=text, reply_markup=markup  )
        await message.delete()
        # media = InputMediaVideo(media=video)
        message_callback = await message.answer_video( video=video,caption=text ,reply_markup=markup)
    else:
        # если нет ни фото, ни видео, изменяем сообщение без медиа
        try:
            if (not message.video) and (not message.video_note):
                await message.delete()
                message_callback = await message.answer( text=text, reply_markup=markup )
            else:
                await message.delete()
                message_callback = await message.answer(text=text, reply_markup=markup)
        except MessageCantBeEdited:
            message_callback = await message.answer(text=text, reply_markup=markup)
        except BadRequest:
            logging.info(text)
            try:
                message_callback = await message.edit_caption(caption=text, reply_markup=markup)
            except MessageToEditNotFound:
                try:
                    await message.delete()
                    message_callback = await message.answer(text=text, reply_markup=markup)
                except MessageToDeleteNotFound:
                    message_callback = await message.answer(text=text, reply_markup=markup)

    if markup:
        if 'inline_keyboard' in markup:
            message.bot['last_message_id'] = message_callback.message_id
