import asyncio
import logging
import textwrap
from math import ceil

import geopy
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
'''
from functools import partial
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="bot_tg")
city = 'Калуга'
geocode = partial(geolocator.geocode, language="ru", query ={'city':city,'county': '', 'country': 'Russia'} )
check_city = geocode()
print( check_city )
try:
    check_city = check_city.raw
    adres_type = check_city['addresstype'] == 'city'
    name_city = check_city['name']
    print(check_city)
    print(name_city)
    print(adres_type)
except AttributeError:
    logging.info('Error')
except TypeError:
    logging.info('Error')
'''

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
city = 'Уфа'
async def test_async(city):
    async with Nominatim(user_agent="bot_tg", adapter_factory=AioHTTPAdapter) as geolocator:
        location = await geolocator.geocode(language='ru', query ={'city':city, 'county': '', 'country': 'Russia'})
        try:
            check_city = location.raw
            adress_type = check_city['addresstype'] == 'city'
            name_city = check_city['name']
            print( check_city )
            print( name_city )
            print( adress_type )
        except AttributeError:
            logging.info( 'Error' )
        except TypeError:
            logging.info( 'Error' )
lll = loop.run_until_complete(test_async('Uf'))