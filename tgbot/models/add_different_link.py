import asyncio
import logging
import textwrap
from math import ceil

from aiogram import types
from aiogram.types import InputMedia

from tgbot.models.engine import create_engine_db, get_session_maker
from tgbot.models.sql_request import insert_users, select_photo

users = {'user_id':465090182, 'name': "asasa",  'user_name':  "salvat3115",   'gender': "women" ,
         'birthday': "2001-01-01" ,  'city': "фывфы" , 'about_me':  "фывфыв", 'partner_another_city':False,
         'min_age':18, 'max_age':23, 'practice': 'Оарарфыраы', 'tabu': 'asdadasdasdas'}
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    engine = create_engine_db( db_path='localhost', db_user='user_bdsm', db_pass='78O89p96', name_db='db_bdsm'  )
#
    session = get_session_maker( engine )
#     for k in range(10):
#         users['user_id'] = users['user_id'] + k+1
#         print(users['user_id'] )
#         lll = loop.run_until_complete( insert_users( session=session, params = users ) )

    more_photos = loop.run_until_complete(select_photo( session=session, user_id=465090182 ))
    quantity_photos = len( more_photos )
    logging.info(more_photos)
    media = types.MediaGroup()
    for photo in more_photos:
        photo_id = InputMedia( media=photo['photo_id'] )
        media.attach_photo( types.InputMediaPhoto( photo_id ))
# Attach local file
# media.attach_photo(types.InputFile('data/cat.jpg'), 'Cat!')
# # More local files and more cats!
# media.attach_photo(types.InputFile('data/cats.jpg'), 'More cats!')
# # You can also use URL's
# # For example: get random puss:
# media.attach_photo('http://lorempixel.com/400/200/cats/', 'Random cat.')
