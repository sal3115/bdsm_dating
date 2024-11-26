import logging
import re
import textwrap
from datetime import datetime, timedelta, date
from math import ceil
from typing import Union, List

from aiogram import types
from aiogram.types import InputMedia, InputMediaVideo
from aiogram.utils.exceptions import MessageCantBeEdited, BadRequest, MessageToEditNotFound, MessageToDeleteNotFound

from tgbot.models.sql_request import select_photo, select_user
from tgbot.services.calculate_age import calculateAge


async def date_formats(dates):
    command_parse = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])[- |/.,](0?[1-9]|1[012])[- |/.,](19|20)\d\d$')
    command_parse_2 = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])[- |/.,](0?[1-9]|1[012])[- |/.,](19|20|21|22|23|24|25)$')
    command_parse_3 = re.compile(r'(^(0?[1-9]|[12][0-9]|3[01])[- /.,](0?[1-9]|1[012]))')
    if re.search(command_parse, dates):
        bad_chars = [',', '.', '-', '_', '/', ' ']
        date1 = ''.join( i for i in dates if not i in bad_chars )
        b = datetime.strptime( date1, '%d%m%Y' ).date()
        return b
    elif re.search(command_parse_2, dates):
        bad_chars = [',', '.', '-', '_', '/', ' ']
        date1 = ''.join( i for i in dates if not i in bad_chars )
        b = datetime.strptime(date1,'%d%m%y').date()
        return b
    else:
        return False


async def date_formats_1(dates):
    dates= datetime.date(dates)
    b = datetime.strptime(dates, '%d%m%Y')
    return b


async def delete_keyboard(message: Union[types.Message, types.CallbackQuery], current_kb=False):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    if current_kb:
        await message.bot.edit_message_reply_markup( chat_id=message.chat.id, message_id=message.message_id)
    else:
        try:
            await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1)
        except:
            pass


# async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
#     if isinstance(message, types.CallbackQuery):
#         message = message.message
#     #TODO мы сохраняли меседж который пришел, а надо тот которыый отправляет т.е на каждый меседж.ансвер присваиваем
#     # одну переменую и с нее сохраняем плюс попробывать сохранять только если был маркап
#     if photo:
#         # если есть фото, изменяем сообщение с фото
#         media = InputMedia(media=photo)
#         if message.photo:
#             try:
#                 await message.edit_media( media=media )
#                 await message.edit_caption( caption=text, reply_markup=markup)
#             except MessageCantBeEdited:
#                 await message.answer_photo(photo=photo, caption=text, reply_markup=markup)
#         else:
#             await message.delete()
#             await message.answer_photo(photo=photo,caption=text, reply_markup=markup)
#     elif video:
#         # если есть видео, изменяем сообщение с видео
#         # await message.edit_caption( caption=text, reply_markup=markup  )
#         await message.delete()
#         # media = InputMediaVideo(media=video)
#         await message.answer_video( video=video,caption=text ,reply_markup=markup)
#     else:
#         # если нет ни фото, ни видео, изменяем сообщение без медиа
#         try:
#             if (not message.video) and (not message.video_note):
#                 await message.delete()
#                 await message.answer( text=text, reply_markup=markup )
#             else:
#                 await message.delete()
#                 await message.answer(text=text, reply_markup=markup)
#         except MessageCantBeEdited:
#             await message.answer(text=text, reply_markup=markup)
#         except BadRequest:
#             logging.info(text)
#             try:
#                 await message.edit_caption(caption=text, reply_markup=markup)
#             except MessageToEditNotFound:
#                 await message.delete()
#                 await message.answer(text=text, reply_markup=markup)
#     message.bot['last_message_id'] = message.message_id

async def text_separator(text, photo = False):
    if photo:
        if len(text) < 1000:
            return [text]
        elif len(text) >= 1000: #len(text) = 2000  |   len(text) = 5000
            return_text = []
            new_text = textwrap.wrap( text, width=1000, break_long_words=True, replace_whitespace=False )
            new_text2 = ' '.join( new_text[1:] )
            if len( new_text2 ) < 4000:
                return new_text[0], new_text2
            else:
                new_text_3 = textwrap.wrap( new_text2, width=4000, break_long_words=True, replace_whitespace=False )
                return_text.append(new_text[0])
                for mess in new_text_3:
                    return_text.append(mess)
                return return_text
    elif len(text) < 4000:
        return text
    elif len( text ) >= 4000:
        new_text = textwrap.wrap( text, width=4000, break_long_words=True, replace_whitespace=False )
        return new_text


async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    if photo:  # если есть фото, изменяем сообщение с фото
        media = InputMedia(media=photo)
        if message.photo:
            logging.info('---------------------------------------')
            await message.edit_media( media=media )
            new_text = await text_separator(text = text, photo=True)
            logging.info(len(new_text))
            if len(new_text) > 1:
                counter = 0
                for mess in new_text:
                    try:
                        if counter == 0:
                            message_callback = await message.edit_caption( caption=mess)
                        else:
                            message_callback = await message.answer( text=mess, reply_markup=markup)
                    except MessageCantBeEdited:
                        message_callback = await message.answer_photo( photo=photo, caption=mess, reply_markup=markup )
                    except BadRequest:
                        message_callback = await message.answer_photo( photo=photo, caption=mess, reply_markup=markup )
            else:
                try:
                    logging.info( '--------------------------------------1' )
                    message_callback = await message.edit_caption( caption=new_text[0],reply_markup=markup )
                except MessageCantBeEdited:
                    logging.info( '--------------------------------------2' )

                    message_callback = await message.answer_photo(photo=photo, caption=new_text[0], reply_markup=markup)
                except BadRequest:
                    logging.info( '--------------------------------------3' )

                    message_callback = await message.answer_photo( photo=photo, caption=new_text[0], reply_markup=markup)
        else:
            new_text = await text_separator(text = text, photo=True)
            logging.info('--------------------------------------8')
            await message.delete()
            if len(new_text) > 1:
                counter = 0
                for mess in new_text:
                    if counter == 0:
                        logging.info( '--------------------------------------1' )
                        message_callback = await message.answer_photo(photo=photo,caption=mess)
                        counter += 1
                    else:
                        logging.info( '--------------------------------------2' )
                        counter += 1
                        if counter == len(new_text):
                            logging.info( '--------------------------------------3' )
                            message_callback = await message.answer(text=mess, reply_markup=markup)
                        else:
                            logging.info( '--------------------------------------4' )
                            message_callback = await message.answer(text=mess)
            else:
                message_callback = await message.answer_photo( photo=photo, caption=new_text[0], reply_markup=markup )
    elif video:
        # если есть видео, изменяем сообщение с видео
        # await message.edit_caption( caption=text, reply_markup=markup  )
        await message.delete()
        # media = InputMediaVideo(media=video)
        message_callback = await message.answer_video( video=video,caption=text ,reply_markup=markup)
    else:
        # если нет ни фото, ни видео, изменяем сообщение без медиа
        try:
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





async def profile_viewer(message:types.Message, text, photo=None, markup=None):
    message.bot['messages_in_loop'] = []
    if photo:
        # если есть фото, изменяем сообщение с фото
        if message.photo:
            media = InputMedia(media=photo)
            await message.edit_media( media=media )
            if len( text ) >= 1000:
                logging.info( len( text ) )
                new_text = textwrap.wrap( text, width=1000, break_long_words=True, replace_whitespace=False )
                message_callback = await message.edit_caption(  caption=new_text[0] )
                message.bot['messages_in_loop'].append( message_callback.message_id )
                counter = 0
                new_text2 = ' '.join( new_text[1:] )
                if len( new_text2 ) < 4000:
                    message_callback = await message.answer( text=new_text2, reply_markup=markup )
                else:
                    new_text_3 = textwrap.wrap( new_text2, width=4000, break_long_words=True, replace_whitespace=False )
                    for mess in new_text_3:
                        counter += 1
                        if counter == len( new_text_3 ):
                            message_callback = await message.answer( text=mess, reply_markup=markup )
                        else:
                            message_callback = await message.answer( text=mess )
                            message.bot['messages_in_loop'].append( message_callback.message_id )
            else:
                message_callback = await message.edit_caption( caption=text, reply_markup=markup )
        else:
            media = InputMedia(media=photo)
            await message.delete()
            if len(text) >= 1000:
                logging.info(len(text))
                new_text = textwrap.wrap( text, width=1000, break_long_words=True, replace_whitespace=False )
                message_callback = await message.answer_photo(photo=photo, caption=new_text[0])
                message.bot['messages_in_loop'].append(message_callback.message_id)
                counter = 0
                new_text2 = ' '.join(new_text[1:])
                if len(new_text2) < 4000:
                    message_callback = await message.answer( text=new_text2, reply_markup=markup )
                else:
                    new_text_3 = textwrap.wrap( new_text2, width=4000, break_long_words=True, replace_whitespace=False )
                    for mess in new_text_3:
                        counter += 1
                        if counter == len(new_text_3):
                            message_callback = await message.answer( text=mess, reply_markup=markup )
                        else:
                            message_callback = await message.answer( text=mess)
                            message.bot['messages_in_loop'].append(message_callback.message_id)
            else:
                message_callback = await message.answer_photo( photo=photo, caption=text, reply_markup=markup )
    elif photo is None:
        if message.photo:
            await message.delete()
            if len(text) > 4000:
                new_text = textwrap.wrap( text, width=4000, break_long_words=True, replace_whitespace=False)
                count = 0
                for text_2 in new_text:
                    count += 1
                    logging.info(f'count {count}')
                    logging.info(f'len(new_text) {len(new_text)}')
                    if count == len(new_text):
                        message_callback = await message.answer( text=text_2, reply_markup=markup )
                    else:
                        message_callback = await message.answer( text=text_2)
                        message.bot['messages_in_loop'].append( message_callback.message_id )

            else:
                message_callback = await message.answer(text=text, reply_markup=markup)
        else:
            if len( text ) >= 4000:
                logging.info( len( text ) )
                new_text = textwrap.wrap( text, width=4000, break_long_words=True, replace_whitespace=False )
                counter = 0
                for mess in new_text :
                    try:
                        if counter == 0:
                            message_callback = await message.edit_text( text=mess )
                            message.bot['messages_in_loop'].append( message_callback.message_id )
                        else:
                            message_callback = await message.answer( text=mess, reply_markup=markup )
                        counter += 1
                    except MessageCantBeEdited as e:
                        await message.delete()
                        message_callback = await message.answer( text=mess, reply_markup=markup )
                    except BadRequest as b:
                        await message.delete()
                        message_callback = await message.answer( text=mess, reply_markup=markup )
            else:
                try:
                    message_callback = await message.edit_text( text=text, reply_markup=markup )
                except MessageCantBeEdited as e:
                    await message.delete()
                    message_callback = await message.answer( text=text, reply_markup=markup )
                except BadRequest as b:
                    await message.delete()
                    message_callback = await message.answer( text=text, reply_markup=markup )
    else:
        logging.info(msg='------------Else---------------')
    if markup:
        if markup.inline_keyboard:
            message.bot['last_message_id'] = message_callback.message_id


async def add_user_func(data):
    params = dict(
        user_id=None,
        status=None,
        first_name=None,
        last_name=None,
        username=None,
        phone_number=None,
        e_mail=None,
        gender=None,
        birthday=None,
        country=None,
        town=None,
        confession=None,
        church=None,
        guarantor=None,
        social_network=None,
        video=None,
        about_my_self=None,
        partner_another_city=None,
        partner_another_town=None,
        partner_another_conf=None,
        min_age=None,
        max_age=None,
    )


async def format_text_profile(anket, session, type_profile=None, reward=None, return_reward=False):
    user_id_anket = anket['user_id']
    id_anket = anket['id']
    name = anket['first_name']
    age = calculateAge( anket['birthday'] )
    city = anket['city']
    last_time = anket['last_time']
    tabu = anket['tabu']
    practices = anket['practices']
    user_info = await select_user(session=session, user_id=user_id_anket)
    text=''
    if type_profile =='favorites_profile':
        text = f'ПОНРАВИЛИСЬ ВАМ\n\n'
    elif type_profile == 'interested_me':
        text = f'ПОНРАВИЛИСЬ ВЫ\n\n'
    elif type_profile == 'mutual_interest':
        text = f'ВЗАИМНЫЙ ИНТЕРЕС\n\n'
    elif type_profile == 'not_interested_me':
        text = f'НЕ ПОНРАВИЛИСЬ ВАМ\n\n'
    text += f'Имя: {name}. Возраст: {age}\n'
    text += f'Город: {city}\n'
    correct_date = last_time.strftime("%d-%m-%Y")
    text += f'Последнее посещение: {correct_date}\n'
    text += f'Желаемые практики: {practices}\n'
    text += f'Табу: {tabu}\n'
    text += f'\n\nНомер анкеты: {id_anket}'

    return text, user_id_anket





async def add_photo_func(photo=None, album: List[types.Message]= None):
    data_photo = []
    if album is not None:
        logging.info(['--------len album--------', album] )
        for enum, obj in enumerate( album ):
            if obj.photo:
                file_id = obj.photo[-1].file_id
                unique_id = obj.photo[-1].file_unique_id
                data_photo.append( {'file_id':file_id, 'unique_id':unique_id} )
            else:
                file_id = obj[obj.content_type].file_id
                unique_id = obj.photo[-1].file_unique_id
                data_photo.append( {'file_id':file_id, 'unique_id':unique_id} )
        return data_photo
    else:
        file_id = photo[-1].file_id
        unique_id = photo[-1].file_unique_id
        logging.info( [file_id, unique_id] )
        data_photo.append({'file_id':file_id, 'unique_id':unique_id})
        return data_photo



