import asyncio

from tgbot.models.engine import create_engine_db, get_session_maker
from tgbot.models.sql_request import insert_users

users = {'user_id':465090182, 'name': "asasa",  'user_name':  "salvat3115",   'gender': "women" ,
         'birthday': "2001-01-01" ,  'city': "фывфы" , 'about_me':  "фывфыв", 'partner_another_city':False,
         'min_age':18, 'max_age':23}
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    engine = create_engine_db( db_path='localhost', db_user='user_bdsm', db_pass='78O89p96', name_db='db_bdsm'  )

    session = get_session_maker( engine )
    for k in range(10):
        users['user_id'] = users['user_id'] + k
        print(users['user_id'] )
        lll = loop.run_until_complete( insert_users( session=session, params = users ) )
