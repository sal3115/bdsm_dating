import logging
from typing import Union

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
# from create_db import get_Confessions
import datetime

from aiogram.utils.callback_data import CallbackData

from tgbot.models.Users import ResendGroupAndChannel
from tgbot.models.sql_request import select_user_name, select_placement_group_channel
from tgbot.services.payment import paid_url


async def func_kb_gender(gender=None):
    kb = InlineKeyboardMarkup()
    if gender != 'men':
        kb.add(InlineKeyboardButton(text='👨‍🦰Мужчина', callback_data=f'men'))
    but_2 = InlineKeyboardButton(text='👩‍🦳Женщина', callback_data=f'women')
    but_3 = InlineKeyboardButton(text='👨‍🦰👩‍🦳Пара', callback_data=f'pair')
    but_4 = InlineKeyboardButton(text='⬅️Назад', callback_data=f'back')

    kb.add(but_2).add(but_3).add(but_4)
    return kb


async def func_kb_back_2(button_next=False):
    text = '🔙Вернуться НАЗАД'
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    but = KeyboardButton(text=text)
    kb.add(but)
    if not button_next:
        return kb
    else:
        next_but_text = 'Пропустить🔜'
        but = KeyboardButton( text=next_but_text )
        kb.add( but )
        return kb

async def new_kb_back(button_back=False,button_next=False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    if button_back:
        text = '🔙Вернуться НАЗАД'
        kb.add( KeyboardButton( text=text ) )
    if button_next:
        next_but_text = 'Пропустить🔜'
        kb.add( KeyboardButton( text=next_but_text ) )
    kb.add(KeyboardButton("Завершить"))
    return kb



async def func_kb_phone(button_next=False, button_complete=False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    but_1 = KeyboardButton(text='Поделиться номером телефона', request_contact=True)
    but_2 = KeyboardButton(text='🔙Вернуться НАЗАД')
    kb.add(but_1).add(but_2)
    if button_next:
        but_3 = KeyboardButton(text='Пропустить🔜')
        kb.add(but_3)
    if button_complete:
        kb.add(KeyboardButton(text='Завершить'))
    return kb


async def func_kb_position(your_position=None):
    kb = InlineKeyboardMarkup()
    if your_position is None or your_position == 'Свитч':
        position_theme = ['Доминирование', 'Подчинение', 'Свитч']
    elif your_position == 'Доминирование':
        position_theme = ['Подчинение', 'Свитч']
    elif your_position == 'Подчинение':
        position_theme = ['Доминирование', 'Свитч']
    else:
        logging.info('Что то пошло не так ')
    for position in position_theme:
        text = position
        but = InlineKeyboardButton(text=text, callback_data=f'{text}')
        kb.add(but)
    return kb


objMonth = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}

d = {
    1: 'Января',
    2: 'Февраля',
    3: 'Марта',
    4: 'Апреля',
    5: 'Мая',
    6: 'Июня',
    7: 'Июля',
    8: 'Августа',
    9: 'Сентября',
    10: 'Октября',
    11: 'Ноября',
    12: 'Декабря'
}
objMonth_rodPad = d
async def func_kb_calendar(cb, _date: datetime.date):
    print(_date)
    _year = _date.year
    _month = _date.month
    _monthName = objMonth[_date.month]
    _date = datetime.date(_year, _month, 1)
    kb = InlineKeyboardMarkup()
    but_1 = InlineKeyboardButton(text='<<<', callback_data=f'backyear_{cb}_{_date.day}-{_date.month}-{_date.year}')
    but_2 = InlineKeyboardButton(text=str(_year), callback_data=f'nothing')
    but_3 = InlineKeyboardButton(text='>>>', callback_data=f'nextyear_{cb}_{_date.day}-{_date.month}-{_date.year}')
    kb.row(but_1, but_2, but_3)
    but_1 = InlineKeyboardButton(text='<<<', callback_data=f'backmonth_{cb}_{_date.day}-{_date.month}-{_date.year}')
    but_2 = InlineKeyboardButton(text=str(_monthName), callback_data=f'nothing')
    but_3 = InlineKeyboardButton(text='>>>', callback_data=f'nextmonth_{cb}_{_date.day}-{_date.month}-{_date.year}')
    kb.row(but_1, but_2, but_3)


    while _date.month == _month:
        i = 1
        print(_date, _date.isoweekday(), i == _date.isoweekday())
        if i == _date.isoweekday() and _date.month == _month:
            b_1 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_1 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        if i == _date.isoweekday() and _date.month == _month:
            b_2 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_2 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        if i == _date.isoweekday() and _date.month == _month:
            b_3 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_3 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        if i == _date.isoweekday() and _date.month == _month:
            b_4 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_4 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        if i == _date.isoweekday() and _date.month == _month:
            b_5 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_5 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        if i == _date.isoweekday() and _date.month == _month:
            b_6 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_6 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        if i == _date.isoweekday() and _date.month == _month:
            b_7 = InlineKeyboardButton(text=_date.day, callback_data=f'{cb}_{_date.day}-{_date.month}-{_date.year}')
            _date = _date + datetime.timedelta(days=1)

        else:
            b_7 = InlineKeyboardButton(text=' ', callback_data=f'nothing')
        i = i + 1

        kb.row(b_1, b_2, b_3, b_4, b_5, b_6, b_7)

    return kb


async def func_kb_look_pravila():
    text = 'Ознакомиться с правилами сообщества'
    kb = InlineKeyboardMarkup()
    but = InlineKeyboardButton(text=text, callback_data='after_start')
    kb.add(but)
    return kb

async def func_kb_acsept_pravila():
    text = 'Хорошо'
    kb = InlineKeyboardMarkup()
    but = InlineKeyboardButton(text=text, callback_data='acseptPravila')
    kb.add(but)
    return kb

async def func_kb_acsept_personal_data():
    text = 'Хорошо'
    kb = InlineKeyboardMarkup()
    but = InlineKeyboardButton(text=text, callback_data='acseptPersonalData')
    kb.add(but)
    return kb

async def func_kb_go_to_anketa():
    text = 'Перейти к анкетированию'
    kb = InlineKeyboardMarkup()
    but = InlineKeyboardButton(text=text, callback_data='goToAnketa')
    kb.add(but)
    return kb

async def func_kb_davayte():
    text = 'Давайте'
    kb = InlineKeyboardMarkup()
    but = InlineKeyboardButton(text=text, callback_data='davayte')
    kb.add(but)
    return kb

yes_no_cb = CallbackData('yes_no_cal_bac', 'callback')

async def yes_no_button():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text='Да',
                                       callback_data=yes_no_cb.new(callback='yes')))
    markup.insert(InlineKeyboardButton(text='Нет',
                                       callback_data= yes_no_cb.new(callback = 'no')))
    return markup


dating_keyboard_favorites_cb= CallbackData('dkfcb', 'callback', 'user_id', 'page')
dating_keyboard_cb= CallbackData('dkcb', 'callback', 'user_id', 'page')
dating_keyboard_interested_me_cb= CallbackData('dkimcb', 'callback', 'user_id', 'page')
dating_keyboard_mutual_interest_cb= CallbackData('dkmicb', 'callback', 'user_id', 'page')
dating_keyboard_not_interested_me_cb= CallbackData('dknimcb', 'callback', 'user_id', 'page')

async def dating_keyboard(user_id=0, page=0, type_profiles=None, url=None, call_back=None):
    logging.info( url )
    if type_profiles == 'favorites_profile':
        callback_data_type = dating_keyboard_favorites_cb
    elif type_profiles == 'interested_me':
        callback_data_type = dating_keyboard_interested_me_cb
    elif type_profiles == 'not_interested_me':
        callback_data_type = dating_keyboard_not_interested_me_cb
    elif type_profiles == 'mutual_interest':
        callback_data_type = dating_keyboard_mutual_interest_cb
    else:
        callback_data_type = dating_keyboard_cb
    markup = InlineKeyboardMarkup(row_width=2)
    if call_back=='about_me':
        markup.add(InlineKeyboardButton(text='Анкета', callback_data=callback_data_type.new(callback='profile',
                                                                                            user_id=user_id,
                                                                                            page=page)))
    else:
        markup.add(InlineKeyboardButton(text='О себе', callback_data=callback_data_type.new(callback='about_me',
                                                                                        user_id=user_id, page=page)))
    # if call_back=='video_card':
    #     markup.add(InlineKeyboardButton(text='📜Анкета', callback_data=callback_data_type.new(callback='profile',
    #                                                                                         user_id=user_id,
    #                                                                                         page=page)))
    # else:
    #     markup.add(InlineKeyboardButton(text='📽Видеовизитка', callback_data=callback_data_type.new(callback='video_card',
    #                                                                                           user_id=user_id, page=page)))
    markup.insert(InlineKeyboardButton(text='Фото',
                                       callback_data=callback_data_type.new(callback='more_photos',
                                                                            user_id=user_id, page=page)))
    if type_profiles == 'mutual_interest':
        if url:
            markup.insert(InlineKeyboardButton(text = 'Написать', url=url,callback_data=callback_data_type.new(callback='write',
                                                                                                   user_id=user_id, page=page)))
    if type_profiles is None or type_profiles == 'interested_me' or type_profiles == 'mutual_interest':
        if call_back == 'interesting':
            markup.insert(
                InlineKeyboardButton( text='Написать', url=url, callback_data=callback_data_type.new( callback='write',
                                                                                                      user_id=user_id,
                                                                                                      page=page ) ) )
        else:
            markup.add(InlineKeyboardButton(text='👍',
                                       callback_data=callback_data_type.new(callback='interesting',
                                                                            user_id=user_id, page=page)))
    if type_profiles == 'not_interested_me':
        markup.insert( InlineKeyboardButton( text='Убрать 👎',
                                             callback_data=callback_data_type.new( callback='remove_dislike',
                                                                                   user_id=user_id, page=page ) ) )
    elif type_profiles == 'favorites_profile':
        markup.insert( InlineKeyboardButton( text='Убрать 👍',
                                             callback_data=callback_data_type.new( callback='remove_like',
                                                                                   user_id=user_id, page=page ) ) )
    else:
        if call_back != 'interesting':
            markup.insert(InlineKeyboardButton(text='👎',
                                       callback_data=callback_data_type.new(callback='dont_show',
                                                                            user_id=user_id, page=page)))

    markup.add(InlineKeyboardButton(text='Жалоба',
                                       callback_data=callback_data_type.new(callback='complain',
                                                                            user_id=user_id, page=page)))
    if type_profiles is not None:
        markup.add( InlineKeyboardButton( text='Назад',
                                             callback_data=callback_data_type.new( callback='back_anket',
                                                                                   user_id=user_id, page=page ) ) )
        markup.insert(InlineKeyboardButton(text='Следующая',
                                           callback_data=callback_data_type.new(callback='following_anket',
                                                                                user_id=user_id, page=page)))
    return markup


interesting_cb= CallbackData('interesting_cal_bac', 'callback', 'user_id' ,'page')

async def favorite_profile_kb(user_id, page):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='Понравились мне', callback_data=interesting_cb.new(callback='liked_them', user_id=user_id, page=page)))
    markup.add(InlineKeyboardButton(text='Не понравились мне', callback_data=interesting_cb.new(callback='not_interested_me', user_id=user_id, page=page)))
    markup.add(InlineKeyboardButton(text='Интересуются мной', callback_data=interesting_cb.new(callback='interested_me', user_id=user_id, page=page)))
    markup.add(InlineKeyboardButton(text='Взаимный интерес', callback_data=interesting_cb.new(callback='mutual_interest', user_id=user_id, page=page)))
    markup.add( InlineKeyboardButton( text='Оформить подписку', callback_data=my_profile_new_cd.new( callback='get_subscribe' ) ) )
    return markup




async def show_recommendations():
    markup = InlineKeyboardMarkup( row_width=1 )
    markup.add(InlineKeyboardButton(text='Показать письмо', callback_data='show_email'))
    return markup


async def ok_recommendation():
    markup = InlineKeyboardMarkup( row_width=1 )
    markup.add( InlineKeyboardButton( text='Ок', callback_data='ok' ) )
    return markup

my_profile_new_cd= CallbackData('mpn_cb', 'callback')
async def my_profile_kb_new(user_id):
    markup = InlineKeyboardMarkup( row_width=1)
    markup.add(InlineKeyboardButton( text='Посмотреть анкету', callback_data=my_profile_new_cd.new( callback='view_profile') ) )
    markup.add(
        InlineKeyboardButton( text='Изменить анкету', callback_data=my_profile_new_cd.new( callback='edit_profile' ) ) )
    markup.add( InlineKeyboardButton( text='Оформить подписку', callback_data=my_profile_new_cd.new( callback='get_subscribe' ) ) )
    return markup


edit_profile_cd= CallbackData('ep_cb', 'callback')
async def edit_profile_kb():
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert(
        InlineKeyboardButton( text='Изменить "о себе"',
                              callback_data=edit_profile_cd.new( callback='edit_about_me' ) ) )
    markup.insert( InlineKeyboardButton( text='Изменить фото',
                                      callback_data=edit_profile_cd.new( callback='edit_photo' ) ) )
    markup.insert(
        InlineKeyboardButton( text='Изменить имя',
                              callback_data=edit_profile_cd.new( callback='edit_name' ) ) )
    markup.insert(
        InlineKeyboardButton( text='Изменить город', callback_data=edit_profile_cd.new( callback='edit_city' ) ) )

    markup.insert(
        InlineKeyboardButton( text='Изменить практики', callback_data=edit_profile_cd.new( callback='edit_practice' ) ) )
    markup.insert(
        InlineKeyboardButton( text='Изменить табу', callback_data=edit_profile_cd.new( callback='edit_tabu' ) ) )
    markup.insert(
        InlineKeyboardButton( text='Изменить дату рождения', callback_data=edit_profile_cd.new( callback='edit_date_birth' ) ) )
    markup.add(
        InlineKeyboardButton( text='Анкеты из другого города?', callback_data=edit_profile_cd.new( callback='edit_another_city' ) ) )
    markup.add(
        InlineKeyboardButton( text='Формат отношений', callback_data=edit_profile_cd.new( callback='edit_interaction_format' ) ) )
    markup.add(
        InlineKeyboardButton( text='Изменить мин и макс возраст',
                              callback_data=edit_profile_cd.new( callback='edit_min_max_age' ) ) )
    markup.add(
        InlineKeyboardButton( text='Назад',
                              callback_data=edit_profile_cd.new( callback='back' ) ) )

    return markup


view_my_profile_cd = CallbackData('view_m_cd', 'callback')
async def view_my_profile_keyboard(call_back=None):
    markup = InlineKeyboardMarkup(row_width=2)
    if call_back=='about_me':
        markup.add(
            InlineKeyboardButton( text='Посмотреть анкету',
                                  callback_data=my_profile_new_cd.new( callback='view_profile' ) ) )
    else:
        markup.add(InlineKeyboardButton(text='📝О себе', callback_data=view_my_profile_cd.new(callback='about_me')))

    # if call_back=='video_card':
    #     markup.add(InlineKeyboardButton(text='Анкета', callback_data=view_my_profile_cd.new(callback='profile')))
    # else:
    #     markup.add(InlineKeyboardButton(text='📽Видеовизитка', callback_data=view_my_profile_cd.new(callback='video_card')))
    markup.add(InlineKeyboardButton(text='📸Еще фото',
                                       callback_data=view_my_profile_cd.new(callback='more_photos')))

    markup.add(
        InlineKeyboardButton( text='Изменить анкету',
                              callback_data=my_profile_new_cd.new( callback='edit_profile' ) ) )
    markup.add( InlineKeyboardButton( text='Оформить подписку',
                                      callback_data=my_profile_new_cd.new( callback='get_subscribe') ) )

    return markup





scrolling_photos_fav_cb = CallbackData('spfcb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_cb = CallbackData('spcb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_inter_me_cb = CallbackData('spimcb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_not_inter_me_cb = CallbackData('spnimcb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_mutual_interest_cb = CallbackData('smicb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_moderation_cd = CallbackData('smcb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_complains_cd = CallbackData('spccb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_main_cd = CallbackData('spmcb', 'callback', 'user_id', 'counter', 'page')
scrolling_photos_search_cd = CallbackData('sp_s_cb', 'callback', 'user_id', 'counter', 'page')

async def scrolling_photos(user_id, page, counter = 0, type_profile=None):
    logging.info(f'---------------{type_profile}-------------')
    if type_profile == 'favorites_profile':
        callback_data_type = scrolling_photos_fav_cb
    elif type_profile == 'interested_me':
        callback_data_type = scrolling_photos_inter_me_cb
    elif type_profile == 'not_interested_me':
        callback_data_type = scrolling_photos_not_inter_me_cb
    elif type_profile == 'mutual_interest':
        callback_data_type = scrolling_photos_mutual_interest_cb
    elif type_profile == 'moderation_profile':
        callback_data_type = scrolling_photos_moderation_cd
    elif type_profile == 'complaints_profile':
        callback_data_type = scrolling_photos_complains_cd
    elif type_profile == 'main_profile':
        callback_data_type = scrolling_photos_main_cd
    elif type_profile == 'search_user':
        callback_data_type = scrolling_photos_search_cd

    else:
        callback_data_type = scrolling_photos_cb
    markup = InlineKeyboardMarkup( row_width=3 )
    markup.insert(
        InlineKeyboardButton( text='Предыдущее фото', callback_data=callback_data_type.new( callback='previous_photo',
                                                                                             user_id=user_id,
                                                                                             counter = counter,
                                                                                             page=page) ) )
    markup.insert(
        InlineKeyboardButton( text='Назад', callback_data=callback_data_type.new( callback='back', user_id=user_id,
                                                                                   counter = counter, page=page) ) )
    markup.insert( InlineKeyboardButton( text='Следующее фото',
                                      callback_data=callback_data_type.new( callback='next_photo', user_id=user_id,
                                                                             counter = counter, page=page ) ) )
    return markup



my_photos_cd = CallbackData('my_photo','callback', 'user_id', 'counter')
async def edit_my_photos_kb(user_id, counter = 0, first_photo=None, no_foto=None):
    markup = InlineKeyboardMarkup( row_width=3 )
    if no_foto:
        markup.add(
            InlineKeyboardButton(text='Добавить фото', callback_data=my_photos_cd.new(callback='add_photo',
                                                                                      user_id=user_id,
                                                                                      counter=counter)))
        return markup
    markup.insert(
        InlineKeyboardButton( text='Предыдущее фото', callback_data=my_photos_cd.new( callback='previous_photo',
                                                                                             user_id=user_id,
                                                                                             counter = counter)))
    markup.insert( InlineKeyboardButton( text='Следующее фото', callback_data=my_photos_cd.new( callback='next_photo',
                                                                                                user_id=user_id,
                                                                                                counter = counter) ) )
    if first_photo:
        markup.add(
            InlineKeyboardButton( text='🟢Назначить главной', callback_data=my_photos_cd.new( callback='assign_main',
                                                                                            user_id=user_id,
                                                                                            counter=counter ) ) )
    else:
        markup.add(InlineKeyboardButton(text='Назначить главной', callback_data=my_photos_cd.new( callback='assign_main',
                                                                                                user_id=user_id,
                                                                                                counter = counter)))
    markup.add(
        InlineKeyboardButton( text='Добавить фото', callback_data=my_photos_cd.new( callback='add_photo',
                                                                                        user_id=user_id,
                                                                                        counter=counter ) ) )
    markup.insert(
        InlineKeyboardButton(text='Удалить фото', callback_data=my_photos_cd.new( callback='delete_photo',
                                                                                        user_id=user_id,
                                                                                        counter=counter ) )
    )
    markup.add(
        InlineKeyboardButton( text='Назад', callback_data=my_photos_cd.new( callback='back', user_id=user_id,
                                                                            counter=counter ) ) )

    return markup

my_video_card_cd = CallbackData('vcc', 'callback' ,'user_id')
async def edit_video_card_kb(user_id, no_video=None):
    markup = InlineKeyboardMarkup( row_width=3 )
    if no_video:
        markup.insert(
            InlineKeyboardButton(text='Добавить', callback_data=my_video_card_cd.new(callback='update_video_card',
                                                                                     user_id=user_id)))
        return markup
    markup.insert( InlineKeyboardButton( text='Изменить', callback_data=my_video_card_cd.new( callback='update_video_card',
                                                                                                user_id=user_id) ) )
    markup.insert(
        InlineKeyboardButton( text='Удалить', callback_data=my_video_card_cd.new( callback='delete_video_card',
                                                                                  user_id=user_id ) ) )
    return markup


verify_user_cd = CallbackData('vucd', 'callback', 'user_id', 'page', 'tp')
async def verify_user_kb(user_id=0, all_info_user=None, page = 0, type_profile=None, call_back=None):
    tp = 0 if type_profile is None else type_profile
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert(
        InlineKeyboardButton( text='Фото', callback_data=verify_user_cd.new( callback='photo', user_id=user_id, page=page, tp=tp ) ) )
    # if call_back =='video':
    #     markup.add( InlineKeyboardButton( text='Анкета', callback_data=verify_user_cd.new( callback='profile',
    #                                                                                             user_id=user_id,
    #                                                                                             page=page, tp=tp ) ) )
    # else:
    #     markup.insert(
    #         InlineKeyboardButton( text='Видеовизитка', callback_data=verify_user_cd.new( callback='video', user_id=user_id, page=page, tp=tp ) ) )
    if call_back == 'about_me':
        markup.add( InlineKeyboardButton( text='Анкета', callback_data=verify_user_cd.new( callback='profile',
                                                                                            user_id=user_id,
                                                                                            page=page, tp=tp ) ) )
    else:
        markup.insert(
            InlineKeyboardButton( text='О себе',
                              callback_data=verify_user_cd.new( callback='about_me', user_id=user_id, page=page, tp=tp ) ) )
    if all_info_user is None or all_info_user['moderation'] == False:
        markup.add(
            InlineKeyboardButton( text='Верифицировать',
                                  callback_data=verify_user_cd.new( callback='verify', user_id=user_id, page=page,
                                                                    tp=tp ) ) )
    if type_profile is None:
        markup.insert(
            InlineKeyboardButton( text='Отклонить', callback_data=verify_user_cd.new( callback='no_verify', user_id=user_id, page=page, tp=tp ) ) )
    elif type_profile == 'search_user':

        markup.insert(
            InlineKeyboardButton( text='Изменить данные',
                                  callback_data=verify_user_cd.new( callback='edit_user', user_id=user_id,
                                                                     page=page, tp=tp ) ) )
    logging.info(all_info_user)
    if type_profile is not None and all_info_user['status'] == 'block':
        markup.add(
            InlineKeyboardButton( text='Разблокировать',
                                  callback_data=verify_user_cd.new( callback='unlock', user_id=user_id, page=page,
                                                                    tp=tp ) ) )
    else:
        markup.add(
            InlineKeyboardButton( text='Заблокировать',
                                  callback_data=verify_user_cd.new( callback='lock', user_id=user_id,
                                                                    page=page, tp=tp ) ) )
    markup.insert(
        InlineKeyboardButton( text='Написать', callback_data=verify_user_cd.new( callback='write', user_id=user_id, page=page, tp=tp ) ) )
    user_link = f'tg://user?id={user_id}'
    markup.insert(
        InlineKeyboardButton( text='Написать по ссылке', url= user_link,
                              callback_data=verify_user_cd.new( callback='write_url', user_id=user_id, page=page,
                                                                tp=tp ) ) )
    if type_profile is None:
        markup.add(
            InlineKeyboardButton( text='Дальше',
                                  callback_data=verify_user_cd.new( callback='next_profile', user_id=user_id, page=page, tp=tp ) ) )
    return markup

edit_user_moderation_cb = CallbackData('eumc', 'callback','user_id_profile')
async def edit_user_moderation_kb(user_id_profile):
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert(
        InlineKeyboardButton( text=f'Изменить имя',
                              callback_data=edit_user_moderation_cb.new( callback='edit_first_name', user_id_profile=user_id_profile) ) )
    markup.insert(
        InlineKeyboardButton( text=f'Изменить фамилию',
                              callback_data=edit_user_moderation_cb.new( callback='edit_last_name', user_id_profile=user_id_profile,) ) )
    markup.insert(
        InlineKeyboardButton( text=f'Назад',
                              callback_data=edit_user_moderation_cb.new( callback='back',
                                                                         user_id_profile=user_id_profile, ) ) )

    return markup

complaints_cd = CallbackData('cmcd', 'callback','com_user_id', 'page')
async def complaints_kb(complaints_user_id, page=0):
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert(
        InlineKeyboardButton( text=f'Посмотреть профиль',
                              callback_data=complaints_cd.new( callback='view_profile', com_user_id=complaints_user_id, page=page ) ) )
    markup.add(
        InlineKeyboardButton( text=f'Заблокировать',
                              callback_data=complaints_cd.new( callback='block', com_user_id=complaints_user_id, page=page ) ) )
    markup.insert(
        InlineKeyboardButton( text='Отклонить',
                              callback_data=complaints_cd.new( callback='reject', com_user_id=complaints_user_id, page=page ) ) )
    markup.add(
        InlineKeyboardButton( text=f'Следующая жалоба',
                              callback_data=complaints_cd.new( callback='next_complaint', com_user_id=complaints_user_id,
                                                               page=page ) ) )

    return markup


complaints_profile_cd = CallbackData('cpcd', 'callback', 'user_id', 'page')
async def complaints_profile_kb(user_id=0, session=None, page = 0):
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert(
        InlineKeyboardButton( text='Фото', callback_data=complaints_profile_cd.new( callback='photo', user_id=user_id, page=page ) ) )
    # markup.insert(
    #     InlineKeyboardButton( text='Видеовизитка', callback_data=complaints_profile_cd.new( callback='video', user_id=user_id, page=page ) ) )
    markup.insert(
        InlineKeyboardButton( text='О себе',
                              callback_data=complaints_profile_cd.new( callback='about_me', user_id=user_id, page=page ) ) )
    user_name = await select_user_name( session, user_id=user_id )
    user_link = f'https://t.me/{user_name[0]["username"]}'
    markup.insert(
        InlineKeyboardButton( text='Написать',url=user_link ,callback_data=complaints_profile_cd.new( callback='', user_id=user_id, page=page ) ) )
    markup.insert(
        InlineKeyboardButton( text='Назад',
                              callback_data=complaints_profile_cd.new( callback='back', user_id=user_id, page=page ) ) )
    return markup


cancel_reward_cd = CallbackData('crcd', 'callback', 'user_id', 'page')
cancel_return_reward_cd = CallbackData('crcd', 'callback', 'user_id', 'page')

async def cancel_reward_inline_kb(user_id=0, page=0, type_reward=None):
    markup = InlineKeyboardMarkup( row_width=3 )
    if type_reward == 'return':
        callback_data_type = cancel_return_reward_cd
    else:
        callback_data_type = cancel_reward_cd
    markup.insert(
        InlineKeyboardButton( text='Уверен',
                              callback_data=callback_data_type.new( callback='confirm', user_id=user_id, page=page ) ) )
    markup.insert(
        InlineKeyboardButton( text='Ошибся', callback_data=callback_data_type.new( callback='wrong', user_id=user_id, page=page ) ) )
    return markup

appoint_moderator_confirm_cd=CallbackData('amcd','callback', 'user_id')
async def appoint_moderator_confirm_kb(user_id):
    markup = InlineKeyboardMarkup( row_width=3 )
    markup.insert(
        InlineKeyboardButton( text='Уверен',
                              callback_data=appoint_moderator_confirm_cd.new( callback='confirm', user_id=user_id) ) )
    markup.insert(
        InlineKeyboardButton( text='Ошибся',
                              callback_data=appoint_moderator_confirm_cd.new( callback='wrong', user_id=user_id) ) )
    return markup


appoint_guarantor_confirm_cd=CallbackData('agcd','callback', 'user_id')
async def appoint_guarantor_confirm_kb(user_id):
    markup = InlineKeyboardMarkup( row_width=3 )
    markup.insert(
        InlineKeyboardButton( text='Уверен',
                              callback_data=appoint_guarantor_confirm_cd.new( callback='confirm', user_id=user_id) ) )
    markup.insert(
        InlineKeyboardButton( text='Ошибся',
                              callback_data=appoint_guarantor_confirm_cd.new( callback='wrong', user_id=user_id) ) )
    return markup


#инлайн клавиатура выход из профиля
exit_profile_cd= CallbackData('epcd','callback', 'user_id')
async def exit_profile_kb(user_id, status_user=None):
    markup = InlineKeyboardMarkup( row_width=1 )
    if status_user == 'user':
        markup.insert(
            InlineKeyboardButton( text='Скрыть анкету',
                                  callback_data=exit_profile_cd.new( callback='hide_profile', user_id=user_id ) ) )
    elif status_user == 'hidden_user':
        markup.insert(
            InlineKeyboardButton(text='Сделать видимой',
                                 callback_data=exit_profile_cd.new(callback='make_visible', user_id=user_id)))
    return markup


#exit_keyboard confirm клавиатурв подтерждение действий выхода
exit_confirm_keyboard_cd= CallbackData('exit_comf_keyb_cd','callback', 'status_user')
async def exit_keyboard_confirm(status_user=None):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(
        InlineKeyboardButton(text='Подтвердить', callback_data=exit_confirm_keyboard_cd.new(callback='confirm', status_user = status_user)))
    markup.insert(
        InlineKeyboardButton(text='Отмена', callback_data=exit_confirm_keyboard_cd.new(callback='cancel', status_user = status_user)))
    return markup


#exit_keyboard confirm клавиатурв подтерждение действий выхода
confirm_restore_account_cd= CallbackData('comf_r_a_cd','callback')
async def confirm_restore_account_kb():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(
        InlineKeyboardButton(text='Да', callback_data=confirm_restore_account_cd.new(callback='yes')))
    markup.insert(
        InlineKeyboardButton(text='Нет', callback_data=confirm_restore_account_cd.new(callback='no')))
    return markup



#different_link_moderation_keyboard
different_link_CD = CallbackData('d_l_cd','callback', 'id_link')
async def different_link_mod_kb(all_info):
    markup = InlineKeyboardMarkup( row_width=1 )
    for info in all_info:
        link = info['link']
        markup.insert(InlineKeyboardButton(text=link, callback_data=different_link_CD.new(callback='existing', id_link=info['id'])))
    markup.insert(InlineKeyboardButton(text='Добавить', callback_data=different_link_CD.new(callback='new', id_link=0)))
    markup.insert(InlineKeyboardButton(text='Отмена', callback_data=different_link_CD.new(callback='cancel', id_link=0)))

    return markup

different_link_edit_descr_or_link_CD = CallbackData('d_l_e_cd','callback', 'id_link')
async def different_link_edit_descr_or_link(id_link):
    markup = InlineKeyboardMarkup( row_width=1 )
    markup.insert(
        InlineKeyboardButton( text='Изменить описание', callback_data=different_link_edit_descr_or_link_CD.new( callback='description', id_link = id_link ) ) )
    markup.insert(
        InlineKeyboardButton( text='Изменить ссылку', callback_data=different_link_edit_descr_or_link_CD.new( callback='link', id_link = id_link ) ) )
    markup.insert(
        InlineKeyboardButton( text='Удалить',
                              callback_data=different_link_edit_descr_or_link_CD.new( callback='delete', id_link=id_link ) ) )
    markup.insert(
        InlineKeyboardButton( text='Отмена', callback_data=different_link_edit_descr_or_link_CD.new( callback='cancel', id_link = 0 ) ) )

    return markup

#Клавиши рекомендаций
recommendation_search_CD = CallbackData('r_s_cd','callback')
async def recommendation_search_kb():
    markup = InlineKeyboardMarkup( row_width=1 )
    markup.insert(
        InlineKeyboardButton( text='Поиск по имени',
                              callback_data=recommendation_search_CD.new( callback='first_name_search',) ) )
    markup.insert(
        InlineKeyboardButton( text='Поиск по фамилии',
                              callback_data=recommendation_search_CD.new( callback='last_name_search') ) )
    markup.insert(
        InlineKeyboardButton( text='Поиск по имени и фамилии',
                              callback_data=recommendation_search_CD.new( callback='first_last_name_search') ) )
    markup.insert(
        InlineKeyboardButton( text='Отмена',
                              callback_data=recommendation_search_CD.new( callback='cancel') ) )
    return markup

async def mailing_kb():
    markup = InlineKeyboardMarkup()

    markup.insert(
        InlineKeyboardButton(text='Сделать рассылку', callback_data='make_newsletter')
    )
    markup.insert(
        InlineKeyboardButton( text='Отмена',
                              callback_data=cancel_cd.new( callback='cancel', user_id=0, page=0) ) )
    return markup


async def search_user_kb():
    markup = InlineKeyboardMarkup()

    markup.insert(
        InlineKeyboardButton(text='Поиск по ИД', callback_data='search_for_id')
    )
    markup.insert(
        InlineKeyboardButton( text='Отмена',
                              callback_data=cancel_cd.new( callback='cancel', user_id=0, page=0) ) )
    return markup


cancel_cd = CallbackData('ccd', 'callback', 'user_id', 'page')
async def cancel_inline_kb(user_id=0, page=0):
    markup = InlineKeyboardMarkup( row_width=3 )
    markup.insert(
        InlineKeyboardButton( text='Отмена', callback_data=cancel_cd.new( callback='cancel', user_id=user_id, page=page ) ) )
    return markup


# paid_subs_cd = CallbackData('pscd', 'id_price', 'user_id')
# async def paid_subs_kb(data ,user_id):
#     markup = InlineKeyboardMarkup( row_width=3 )
#     for dat in data:
#         await paid_url( user_id=user_id, id_rate=dat['id'],  )
#         markup.insert(InlineKeyboardButton( text=f'{dat["title"]}', callback_data= paid_subs_cd.new(id_price = dat['id'], user_id=user_id) ) )
#     return markup

async def paid_subs_kb(data ,user_id):
    markup = InlineKeyboardMarkup( row_width=3 )
    for dat in data:
        url_paid = await paid_url( user_id=user_id, id_rate=dat['id'],  amount=dat['price'])
        markup.insert(InlineKeyboardButton( text=f'{dat["title"]}', url= url_paid) )
    return markup
yes_no_cb_new = CallbackData('yncn', 'callback')
async def yes_no_kb():
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert( InlineKeyboardButton( text='Да',
                                         callback_data=yes_no_cb_new.new( callback='yes' ) ) )
    markup.insert( InlineKeyboardButton( text='Нет',
                                         callback_data=yes_no_cb_new.new( callback='no' ) ) )
    return markup


interaction_format_cb = CallbackData('ifcb', 'callback')

async def interaction_format_button():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text='Оффлайн',
                                       callback_data=interaction_format_cb.new(callback='offline')))
    markup.insert(InlineKeyboardButton(text='Онлайн',
                                       callback_data= interaction_format_cb.new(callback = 'online')))
    markup.insert( InlineKeyboardButton( text='Оба',
                                         callback_data=interaction_format_cb.new( callback='all' ) ) )
    return markup

yes_no_cb_confirm_city = CallbackData('ynccc', 'callback')
async def yes_no_kb_confirm_city():
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert( InlineKeyboardButton( text='Да',
                                         callback_data=yes_no_cb_confirm_city.new( callback='yes' ) ) )
    markup.insert( InlineKeyboardButton( text='Нет',
                                         callback_data=yes_no_cb_confirm_city.new( callback='no' ) ) )
    return markup

test_keyboard_cd = CallbackData('tkcd', 'callback')
async def test_keyboard():
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert( InlineKeyboardButton( text='test',
                                         callback_data=test_keyboard_cd.new(callback='test') ) )
    return markup

resend_group_keyboard_cd =  CallbackData('rgkcd', 'id_channel', 'action', 'anonymous')
async def resend_group_keyboard(all_group, selected:set, anonymous):
    markup = InlineKeyboardMarkup( row_width=2 )
    for group in all_group:
        id_channel = str(group['id'])
        logging.info(f'id_channel {type(id_channel)} - {id_channel}')
        for s in selected:
            logging.info(f'selected {type(s)} - {s}')
        text = f"{'✅ ' if id_channel in selected else ''}{group['title_channel_group']}"
        markup.add( InlineKeyboardButton( text=text,
                                             callback_data=resend_group_keyboard_cd.new(id_channel=id_channel, action='toggle', anonymous=anonymous) ) )

    markup.add( InlineKeyboardButton(text=f'{"✅ " if anonymous else ""}Анонимное размещение', callback_data=resend_group_keyboard_cd.new(id_channel=0, action='anonymous',anonymous=anonymous)))
    markup.add( InlineKeyboardButton(text='🚫Нет, не хочу', callback_data=resend_group_keyboard_cd.new(id_channel=0, action='cancel',anonymous=anonymous)))
    markup.insert( InlineKeyboardButton(text='Готово', callback_data=resend_group_keyboard_cd.new(id_channel=0, action='done', anonymous=anonymous)))
    return markup



confirm_resend_platform_cd = CallbackData('crpcd', 'callback')
async def confirm_resend_platform():
    markup = InlineKeyboardMarkup( row_width=2 )
    markup.insert( InlineKeyboardButton( text='Да',
                                         callback_data=confirm_resend_platform_cd.new(callback='yes') ) )
    markup.insert( InlineKeyboardButton( text='Нет',
                                         callback_data=confirm_resend_platform_cd.new( callback='no' ) ) )
    return markup

