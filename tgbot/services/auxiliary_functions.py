import asyncio
import logging
import re
import textwrap
from datetime import datetime, timedelta, date
from math import ceil
from typing import Union, List

from aiogram import types
from aiogram.bot import bot
from aiogram.types import InputMedia, InputMediaVideo, InputFile, InputMediaPhoto
from aiogram.utils.exceptions import MessageCantBeEdited, BadRequest, MessageToEditNotFound, MessageToDeleteNotFound, \
    MessageNotModified, InlineKeyboardExpected
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter

from tgbot.config import load_config
from tgbot.models.engine import create_engine_db, get_session_maker
from tgbot.models.sql_request import select_photo, select_user, select_check_mutual_interest, \
    select_check_daily_interest, insert_like_dis, insert_daily_reaktion, select_check_interest, delete_daily_reaction, \
    delete_reaction_like_dislike_table
from tgbot.services.calculate_age import calculateAge

async def check_city(city):
    async with Nominatim(user_agent="bot_tg", adapter_factory=AioHTTPAdapter) as geolocator:
        location = await geolocator.geocode(language='ru', query ={'city':city, 'county': '', 'country': 'Russia'})
        try:
            check_city = location.raw
            adress_type = check_city['addresstype'] == 'city'
            name_city = check_city['name']
            return adress_type, name_city
        except AttributeError:
            return False
        except TypeError:
            return False
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
        return [text]
    elif len( text ) >= 4000:
        new_text = textwrap.wrap( text, width=4000, break_long_words=True, replace_whitespace=False )
        return new_text


async def edit_message_2(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    if photo:  # если есть фото, изменяем сообщение с фото
        media = InputMedia(media=photo)
        if message.photo:
            logging.info('---------------------------------------')
            try:
                await message.edit_media( media=media )
            except BadRequest:
                pass
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
            try:
                logging.info( '--------------------------------------8_1' )
                await message.delete()
            except MessageToDeleteNotFound:
                logging.info( '--------------------------------------8_2' )
                pass
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

# async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
#     callback = message
#     # if isinstance(message, types.CallbackQuery):
#     #     message = message.message
#     logging.info(f'message {message}, photo {photo}')
#     if photo:  # если есть фото, изменяем сообщение с фото
#         media = InputMedia(media=photo)
#         try:
#             last_message = message.bot["last_message"]
#         except KeyError:
#             last_message = message
#         if last_message is not None:
#             new_text = await text_separator(text = text, photo=True)
#             logging.info(f'{message.message_id} - {last_message.message_id}')
#             logging.info(message)
#             logging.info(last_message)
#
#             if len(new_text) == 1:
#                 await message.delete()
#                 message_callback = await message.bot.edit_message_media(media=media, chat_id=message.chat.id, message_id=last_message.message_id,reply_markup=markup)
#                 message_callback = await message.bot.edit_message_caption(caption=text, chat_id=message.chat.id, message_id=last_message.message_id,reply_markup=markup)
#         else: #если в текущем сообщении хотим отправить фото и в последнем сообщении не было фото
#             if last_message is not None:
#                 try:
#                     message_callback = await message.bot.edit_message_media( media=media, chat_id=message.chat.id,
#                                                                          message_id=last_message.message_id )
#                     message_callback = await message.bot.edit_message_caption(caption=text, chat_id=message.chat.id,
#                                                                               message_id=last_message.message_id,reply_markup=markup)
#
#                 except BadRequest as e:
#                     logging.info(e)
#                     message_callback = await message.bot.send_photo( photo=photo, chat_id=message.chat.id,
#                                                                              reply_markup=markup, caption=text )
#                 await message.delete()
#
#             else:
#                 logging.info('33333333333333333333')
#     elif video:
#         # если есть видео, изменяем сообщение с видео
#         # await message.edit_caption( caption=text, reply_markup=markup  )
#         await message.delete()
#         # media = InputMediaVideo(media=video)
#         message_callback = await message.answer_video( video=video,caption=text ,reply_markup=markup)
#     else:
#         # если нет ни фото, ни видео, изменяем сообщение без медиа
#         try:
#             last_message = message.bot["last_message"]
#             logging.info(last_message)
#             last_message:types.Message
#         except KeyError:
#             last_message = message
#             if last_message.photo:
#                 await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message.message_id)
#                 logging.info(text)
#                 message_callback = await message.answer(text=text, reply_markup=markup)
#             else:
#                 if last_message.reply_markup:
#                     try: #в тот момент когда не было клавы у последнего сообщения, а данные в last_message остались от предполеднего
#                         await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=last_message.message_id)
#                     except (MessageNotModified, MessageToEditNotFound) as e:
#                         logging.info(e)
#                 new_text = await text_separator(text = text, photo=True)
#                 try:
#                     if len(new_text) == 1:
#                         # try:
#                         if 'entities' in message:
#                             message_callback = await message.answer(text=text, reply_markup=markup)
#                         else:
#                             await message.delete()
#                             message_callback = await message.bot.edit_message_text(text=text, chat_id=message.chat.id,
#                                                                    message_id=last_message.message_id, reply_markup=markup)
#                         # except InlineKeyboardExpected:
#                         #     message_callback = await message.bot.edit_message_text( text=text, chat_id=message.chat.id,
#                         #                                                             message_id=last_message.message_id)
#                     else:
#                         counter = 0
#                         for mess in new_text:
#                             if counter == 0:
#                                 message_callback = await message.bot.edit_message_text( text=mess,
#                                                                                         chat_id=message.chat.id,
#                                                                                         message_id=last_message.message_id )
#                                 counter+= 1
#                             elif counter == len(new_text):
#                                 message_callback = await message.bot.send_message( text=mess, chat_id=message.chat.id,
#                                                                                    reply_markup=markup )
#                             else:
#                                 message_callback = await message.bot.send_message( text=mess, chat_id=message.chat.id,
#                                                                                    )
#                                 counter += 1
#
#                 except MessageToEditNotFound:
#                     if len(new_text) == 1:
#                         message_callback = await message.bot.send_message( text=text, chat_id=message.chat.id,
#                                                                                 reply_markup=markup )
#                     else:
#                         counter = 0
#                         for mess in new_text:
#                             counter+=1
#                             if counter == len( new_text ):
#                                 message_callback = await message.bot.send_message( text=mess, chat_id=message.chat.id,
#                                                                                    reply_markup=markup )
#                             else:
#                                 message_callback = await message.bot.send_message( text=mess, chat_id=message.chat.id,
#                                                                                    )
#     message.bot['last_message'] = message_callback
#
#     # try:
#     #     if message_callback.reply_markup:
#     #         if 'inline_keyboard' in markup:
#     #             message.bot['last_message'] = message_callback
#     # except UnboundLocalError:
#     #     if markup:
#     #         if 'inline_keyboard' in markup:
#     #             message.bot['last_message'] = message_callback



# async def profile_viewer(message:types.Message, text, photo=None, markup=None):
#     message.bot['messages_in_loop'] = []
#     if photo:
#         # если есть фото, изменяем сообщение с фото
#         if message.photo:
#             media = InputMedia(media=photo)
#             await message.edit_media( media=media )
#             if len( text ) >= 1000:
#                 logging.info( len( text ) )
#                 new_text = textwrap.wrap( text, width=1000, break_long_words=True, replace_whitespace=False )
#                 message_callback = await message.edit_caption(  caption=new_text[0] )
#                 message.bot['messages_in_loop'].append( message_callback.message_id )
#                 counter = 0
#                 new_text2 = ' '.join( new_text[1:] )
#                 if len( new_text2 ) < 4000:
#                     message_callback = await message.answer( text=new_text2, reply_markup=markup )
#                 else:
#                     new_text_3 = textwrap.wrap( new_text2, width=4000, break_long_words=True, replace_whitespace=False )
#                     for mess in new_text_3:
#                         counter += 1
#                         if counter == len( new_text_3 ):
#                             message_callback = await message.answer( text=mess, reply_markup=markup )
#                         else:
#                             message_callback = await message.answer( text=mess )
#                             message.bot['messages_in_loop'].append( message_callback.message_id )
#             else:
#                 message_callback = await message.edit_caption( caption=text, reply_markup=markup )
#         else:
#             media = InputMedia(media=photo)
#             await message.delete()
#             if len(text) >= 1000:
#                 logging.info(len(text))
#                 new_text = textwrap.wrap( text, width=1000, break_long_words=True, replace_whitespace=False )
#                 message_callback = await message.answer_photo(photo=photo, caption=new_text[0])
#                 message.bot['messages_in_loop'].append(message_callback.message_id)
#                 counter = 0
#                 new_text2 = ' '.join(new_text[1:])
#                 if len(new_text2) < 4000:
#                     message_callback = await message.answer( text=new_text2, reply_markup=markup )
#                 else:
#                     new_text_3 = textwrap.wrap( new_text2, width=4000, break_long_words=True, replace_whitespace=False )
#                     for mess in new_text_3:
#                         counter += 1
#                         if counter == len(new_text_3):
#                             message_callback = await message.answer( text=mess, reply_markup=markup )
#                         else:
#                             message_callback = await message.answer( text=mess)
#                             message.bot['messages_in_loop'].append(message_callback.message_id)
#             else:
#                 message_callback = await message.answer_photo( photo=photo, caption=text, reply_markup=markup )
#     elif photo is None:
#         if message.photo:
#             await message.delete()
#             if len(text) > 4000:
#                 new_text = textwrap.wrap( text, width=4000, break_long_words=True, replace_whitespace=False)
#                 count = 0
#                 for text_2 in new_text:
#                     count += 1
#                     logging.info(f'count {count}')
#                     logging.info(f'len(new_text) {len(new_text)}')
#                     if count == len(new_text):
#                         message_callback = await message.answer( text=text_2, reply_markup=markup )
#                     else:
#                         message_callback = await message.answer( text=text_2)
#                         message.bot['messages_in_loop'].append( message_callback.message_id )
#
#             else:
#                 message_callback = await message.answer(text=text, reply_markup=markup)
#         else:
#             if len( text ) >= 4000:
#                 logging.info( len( text ) )
#                 new_text = textwrap.wrap( text, width=4000, break_long_words=True, replace_whitespace=False )
#                 counter = 0
#                 for mess in new_text :
#                     try:
#                         if counter == 0:
#                             message_callback = await message.edit_text( text=mess )
#                             message.bot['messages_in_loop'].append( message_callback.message_id )
#                         else:
#                             message_callback = await message.answer( text=mess, reply_markup=markup )
#                         counter += 1
#                     except MessageCantBeEdited as e:
#                         await message.delete()
#                         message_callback = await message.answer( text=mess, reply_markup=markup )
#                     except BadRequest as b:
#                         await message.delete()
#                         message_callback = await message.answer( text=mess, reply_markup=markup )
#             else:
#                 try:
#                     message_callback = await message.edit_text( text=text, reply_markup=markup )
#                 except MessageCantBeEdited as e:
#                     await message.delete()
#                     message_callback = await message.answer( text=text, reply_markup=markup )
#                 except BadRequest as b:
#                     await message.delete()
#                     message_callback = await message.answer( text=text, reply_markup=markup )
#     else:
#         logging.info(msg='------------Else---------------')
#     if markup:
#         if markup.inline_keyboard:
#             message.bot['last_message'] = message_callback

async def send_message_callback(callback:types.CallbackQuery, text, last_message, photo=None, markup=None, type_viewer=None):
    last_message: types.Message
    new_last_message = None
    if photo or type_viewer =='profile_viewer': # Photo
        answer_photo = photo if photo else InputFile('tgbot/misc/no_photo.jpg')
        if last_message is not None: # есть last_message
            if 'photo' in last_message :  # в last_message есть фото
                try:
                    media = InputMedia( media=photo ) if photo else InputMediaPhoto(
                        media=InputFile( 'tgbot/misc/no_photo.jpg' ) )
                    logging.info( f'media {media} - type {type( media )}' )
                    logging.info( f'photo {photo} - type {type( photo )}' )
                    await callback.bot.edit_message_media( media=media, chat_id=callback.message.chat.id,
                                                          message_id=last_message.message_id )
                    new_last_message = await callback.bot.edit_message_caption( caption=text, chat_id=callback.message.chat.id,
                                                                               message_id=last_message.message_id,
                                                                               reply_markup=markup )
                    if last_message.message_id != callback.message.message_id:
                        await callback.bot.delete_message( chat_id=callback.message.chat.id, message_id=callback.message.message_id )
                except (MessageToEditNotFound, MessageToDeleteNotFound):
                    new_last_message = await callback.message.answer_photo( photo=answer_photo, caption=text,
                                                                   reply_markup=markup )
        else: # нет last_message
            new_last_message = await callback.message.answer_photo( photo=photo, caption=text, reply_markup=markup )
    else: # no photo
        if last_message is not None: # есть last_message
            if 'photo' in last_message : # в last_message есть фото
                try:
                    await callback.bot.delete_message( chat_id=callback.message.chat.id,
                                                       message_id=last_message.message_id )
                    new_last_message = await callback.message.answer(text=text, reply_markup=markup)
                except( MessageToEditNotFound, MessageToDeleteNotFound):
                    await callback.message.answer(text=text, reply_markup=markup)
            else: # в last_message нет фото
                if last_message.message_id + 2 > callback.message.message_id:
                    await callback.message.delete()
                    new_last_message = await callback.message.answer( text=text, reply_markup=markup )
                else:
                    await callback.message.delete()
                    new_last_message = await callback.bot.edit_message_text( text=text, chat_id=callback.message.chat.id,
                                                                            message_id=last_message.message_id,
                                                                            reply_markup=markup )
        else:# no last_message
            new_last_message = await callback.message.answer( text=text, reply_markup=markup )
    return new_last_message


async def send_message_message(message:types.Message, text, last_message, photo=None, markup=None, type_viewer=None):
    last_message: types.Message
    new_last_message = None
    if photo or type_viewer == 'profile_viewer':  # Photo
        answer_photo = photo if photo else InputFile('tgbot/misc/no_photo.jpg')
        if last_message is not None: # есть last_message
            if 'photo' in last_message :  # в last_message есть фото
                try:
                    media = InputMedia(media=photo) if photo else InputMediaPhoto( media=InputFile('tgbot/misc/no_photo.jpg'))
                    logging.info(f'media {media} - type {type(media)}')
                    logging.info(f'photo {photo} - type {type(photo)}')
                    await message.bot.edit_message_media(media=media, chat_id=message.chat.id, message_id=last_message.message_id)
                    new_last_message = await message.bot.edit_message_caption(caption=text, chat_id=message.chat.id, message_id=last_message.message_id, reply_markup=markup)
                    if last_message.message_id != message.message_id:
                        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                except (MessageToEditNotFound, MessageToDeleteNotFound):
                    new_last_message = await message.answer_photo( photo=answer_photo, caption=text, reply_markup=markup )
            else:  # в last_message нет фото
                try:
                    await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message.message_id)
                    new_last_message = await message.answer_photo(photo=answer_photo, caption=text, reply_markup=markup)
                except ( MessageToEditNotFound, MessageToDeleteNotFound):
                    new_last_message = await message.answer_photo( photo=answer_photo, caption=text, reply_markup=markup )
        else: # нет last_message
            new_last_message = await message.answer_photo( photo=answer_photo, caption=text, reply_markup=markup )
    else: # no photo
        if last_message is not None: # есть last_message
            logging.info(last_message)
            if 'photo' in last_message : # в last_message есть фото
                try:

                    await message.bot.delete_message( chat_id=message.chat.id,
                                                   message_id=last_message.message_id )
                    new_last_message = await message.answer(text=text, reply_markup=markup)
                except(MessageToEditNotFound, MessageToDeleteNotFound):
                    new_last_message = await message.answer( text=text, reply_markup=markup )
            else: # в last_message нет фото
                try:
                    if 'reply_markup' in last_message and 'reply_markup' in message:
                        new_last_message = await message.bot.edit_message_text( text=text,chat_id=message.chat.id, message_id=last_message.message_id, reply_markup=markup )
                    else:
                        if 'reply_markup' in last_message:
                            await message.bot.delete_message(chat_id=message.chat.id, message_id=last_message.message_id)
                        new_last_message = await message.answer( text=text, reply_markup=markup )
                        await message.delete()
                except( MessageToEditNotFound, MessageToDeleteNotFound):
                    new_last_message = await message.answer( text=text, reply_markup=markup )
        else:# no last_message
            new_last_message = await message.answer( text=text, reply_markup=markup )
    return new_last_message


# async def profile_viewer(message:Union[types.Message, types.CallbackQuery], text, photo=None, markup=None):
#     #     new_text =
#     try:
#         last_message = message.bot['last_message']
#     except KeyError:
#         last_message = None
#     if isinstance(message, types.CallbackQuery):
#         message_callback = await send_message_callback(callback=message,text=text ,last_message=last_message, photo=photo, markup=markup, type='profile_viewer')
#     else: #types.Message
#         message_callback = await send_message_message(message=message, text=text, last_message=last_message, photo=photo, markup=markup, type='profile_viewer')
#     if markup:
#         if markup.inline_keyboard:
#             message.bot['last_message'] = message_callback

async def profile_viewer(message:Union[types.Message, types.CallbackQuery], text, photo=None, markup=None):
    new_text = await text_separator(text=text, photo=photo)
    logging.info(len(new_text))
    message_callback = None
    try:
        last_message = message.bot['last_message']
    except KeyError:
        last_message = None
    if isinstance(message, types.CallbackQuery):
        if len(new_text) <=1:
            message_callback = await send_message_callback(callback=message,text=text ,last_message=last_message, photo=photo, markup=markup, type_viewer='profile_viewer')
        else:
            counter = 1
            for n_t in new_text:
                if counter == 1:
                    message_callback = await send_message_callback( callback=message, text=n_t, last_message=last_message,
                                                                photo=photo, type_viewer='profile_viewer' )
                    counter+=1
                elif counter == len(new_text):
                    message_callback = await send_message_callback( callback=message, text=n_t,
                                                                    last_message=last_message,
                                                                    markup=markup, type_viewer='profile_viewer' )
                    return
                else:
                    message_callback = await send_message_callback( callback=message, text=n_t,
                                                                    last_message=last_message, type_viewer='profile_viewer' )
                    counter+=1
    else: #types.Message
        if len(new_text) <=1:
            message_callback = await send_message_message(message=message, text=text, last_message=last_message, photo=photo, markup=markup, type_viewer='profile_viewer')
        else:
            counter = 1
            for n_t in new_text:
                if counter == 1:
                    message_callback = await send_message_message( message=message, text=n_t, last_message=last_message,
                                                               photo=photo, type_viewer='profile_viewer' )
                elif counter == len(new_text):
                    message_callback = await send_message_message( message=message, text=n_t, last_message=last_message,
                                                                   markup=markup, type_viewer='profile_viewer' )
                    return
                else:
                    message_callback = await send_message_message( message=message, text=n_t, last_message=last_message,
                                                                   type_viewer='profile_viewer' )
    if markup:
        if markup.inline_keyboard:
            message.bot['last_message'] = message_callback


# async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
#     new_text =
#     try:
#         last_message = message.bot['last_message']
#     except KeyError:
#         last_message = None
#     if isinstance(message, types.CallbackQuery):
#         message_callback = await send_message_callback(callback=message,text=text ,last_message=last_message, photo=photo, markup=markup)
#     else: #types.Message
#         message_callback = await send_message_message(message=message, text=text, last_message=last_message, photo=photo, markup=markup)
#     if markup:
#         logging.info(markup)
#         if markup.inline_keyboard:
#             message.bot['last_message'] = message_callback
async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
    new_text = await text_separator(text=text, photo=photo)
    logging.info(len(new_text))
    try:
        last_message = message.bot['last_message']
    except KeyError:
        last_message = None
    if isinstance(message, types.CallbackQuery):
        if len(new_text) <= 1:
            message_callback = await send_message_callback(callback=message,text=text ,last_message=last_message, photo=photo, markup=markup)
        else:
            counter = 1
            for n_t in new_text:
                if counter == 1:
                    message_callback = await send_message_callback( callback=message, text=n_t,
                                                                    last_message=last_message,
                                                                    photo=photo)
                    counter += 1
                elif counter == len( new_text ):
                    message_callback = await send_message_callback( callback=message, text=n_t,
                                                                    last_message=last_message,
                                                                    markup=markup)
                    return
                else:
                    message_callback = await send_message_callback( callback=message, text=n_t,
                                                                    last_message=last_message)
                    counter += 1
    else: #types.Message
        if len(new_text) <=1:
            message_callback = await send_message_message(message=message, text=text, last_message=last_message, photo=photo, markup=markup)
        else:
            counter = 1
            for n_t in new_text:
                if counter == 1:
                    message_callback = await send_message_message( message=message, text=n_t, last_message=last_message,
                                                                   photo=photo)
                elif counter == len( new_text ):
                    message_callback = await send_message_message( message=message, text=n_t, last_message=last_message,
                                                                   markup=markup)
                    return
                else:
                    message_callback = await send_message_message( message=message, text=n_t, last_message=last_message)
    if markup:
        if 'inline_keyboard' in markup:
            message.bot['last_message'] = message_callback
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
    interaction_format_russia = {'offline': 'Оффлайн', 'online': 'Онлайн','all': 'Любой'}
    tru_false_russia = {'True': 'Да', 'False': 'Нет'}
    gender_russia = {'men': 'муж.', 'women': 'жен.', 'pair':'пара'}
    user_id_anket = anket['user_id']
    id_anket = anket['id']
    name = anket['first_name']
    age = await calculateAge( anket['birthday'] )
    city = anket['city']
    last_time = anket['last_time']
    tabu = anket['tabu']
    practices = anket['practices']
    interaction_format = anket['interaction_format']
    gender = anket['gender']
    gender_partner = anket['gender_partner']
    my_position = anket['your_position']
    partner_position = anket['partner_position']
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
    text += f'Пол: {gender_russia[f"{gender}"]}. Ищю пол: {gender_russia[f"{gender_partner}"]}\n'
    text += f'Моя позиция: {my_position}.\n'
    text += f'Ищу позицию: {partner_position}.\n'
    text += f'Город: {city}\n'
    correct_date = last_time.strftime("%d-%m-%Y")
    text += f'Последнее посещение: {correct_date}\n'
    text += f'Желаемый формат: {interaction_format_russia[f"{interaction_format}"]}\n'
    text += f'Желаемые практики: {practices}\n'
    text += f'Табу: {tabu}\n'
    text += f'\n\nНомер анкеты: {id_anket}'
    if type_profile == 'main_profile':
        partner_another_city = anket['partner_another_city']
        min_age = anket['min_age']
        max_age = anket['max_age']
        moderation = anket['moderation']
        text+= f'\nПартнер из другого города: {tru_false_russia[str(partner_another_city)]}'
        text+= f'\nМинимальный возраст: {min_age}'
        text +=f'\nМаксимальный возраст {max_age}'
        text+= f'\nМодерация: {tru_false_russia[str(moderation)]}'

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


async def check_like_dislike(session, user_id, partner_user_id, rection):
    check_mutual_like = await select_check_mutual_interest( session=session, user_id=user_id,
                                                            partner_id=partner_user_id )
    if len(check_mutual_like)>=1:
        return False
    else:
        return True


async def insert_like_dislake_all(session, user_id, partner_user_id, reaction):
    check_mutual_like = await select_check_interest( session=session, user_id=user_id,
                                                            partner_id=partner_user_id )
    check_daily_like = await select_check_daily_interest(session=session, user_id=user_id,
                                                            partner_id=partner_user_id )
    if len(check_mutual_like) <= 0 and len(check_daily_like) <= 0 :
        await insert_like_dis( session=session, user_id=user_id,
                                                            partner_id=partner_user_id, reaction=reaction)
        await insert_daily_reaktion(session=session, user_id=user_id,
                                                            partner_id=partner_user_id, reaction=reaction)
    elif len(check_mutual_like) >= 1 and len( check_daily_like ) <= 0 :
        await insert_daily_reaktion( session=session, user_id=user_id,
                                     partner_id=partner_user_id, reaction=reaction )
    elif len( check_daily_like ) >= 1 and len(check_mutual_like) <= 0:
        await insert_like_dis( session=session, user_id=user_id,
                                     partner_id=partner_user_id, reaction=reaction )
    else:
        return

# async def creating_bill(data, user_id):
#     all_info = []
#     for dat in data:
#         quickpay = Quickpay(
#             receiver="410012030256059",
#             quickpay_form="shop",
#             targets="subscription_bot",
#             paymentType="SB",
#             sum=int(dat["price"]),
#             label=f'{user_id}-{dat["title"]}-{int(dat["price"])}'
#         )
#         url_paid = quickpay.redirected_url
#         all_info.append({'title': dat["title"], 'price': int(dat["price"]), 'url_paid': url_paid})
#     return all_info

async def clear_table():
    config = load_config(".env")
    engine = create_engine_db( db_path=config.db.host, db_pass=config.db.db_pass, db_user=config.db.db_user,
                               name_db=config.db.db_name )
    session = get_session_maker( engine )
    await delete_daily_reaction(session=session)
    await delete_reaction_like_dislike_table(session=session)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    lll = loop.run_until_complete( clear_table() )

async def shedule_jobs():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_table, 'cron', day_of_week='mon-sun', hour=00, minute=00,)
    scheduler.start()