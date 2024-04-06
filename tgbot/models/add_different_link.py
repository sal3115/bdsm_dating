import asyncio

from tgbot.models.engine import create_engine_db, get_session_maker
from tgbot.models.sql_request import insert_different_links, insert_conf

link_diffs = [{'link':'https://youtube.com/@pyataykins', 'description':'Ютуб канал о семейных ценностях "Пятайкины". Тут множество отличных примеров крепких и счастливых семей у которых можно многому научиться! '},
              {'link':'https://pyataykins.com/course', 'description':'Пройдите онлайн курс "Как найти того самого человека с которым я смогу построить крепкую семью" и начните строить отношения по правильным принципам!'},
              {'link':'https://t.me/+SKzVxMaw2GExNTUy ', 'description':'Закрытый христианский клуб Юлии Пятайкиной "Изнутри наружу" Это сообщество для девушек-христианок в котором мы вместе отказываемся от сахара, общаемся, тренируемся духом и телом. Как говорят участницы: "У вас тут так душевно, я нигде такой атмосферы поддержки и принятия не встречала!"'},
              {'link':'http://pyataykin.tilda.ws/', 'description':'Антон Пятайкин - Ведущий на ваше мероприятие, свадьбу, корпоратив или бизнес событие. Дорого. '}]

confessions = ['Баптисты', 'Пятидесятники', 'Харизматы', 'Евангелисты', 'Адвентисты', 'Англикане',
                   'Кальвинисты', 'Лютеране', 'Методисты', 'Пресвитериане']

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    engine = create_engine_db( '/tgbot/models/db_datingBot.sqlite' )
    session = get_session_maker( engine )
    for l in link_diffs:
        link = l['link']
        description = l['description']
        lll = loop.run_until_complete( insert_different_links( session=session, link=link, description=description ) )
    for conf in confessions:
        lll = loop.run_until_complete( insert_conf( session=session, confession=conf) )
