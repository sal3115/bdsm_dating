import logging
import re
from datetime import datetime, timedelta, date
from typing import Union, List

from aiogram import types
from aiogram.types import InputMedia, InputMediaVideo
from aiogram.utils.exceptions import MessageCantBeEdited, BadRequest, MessageToEditNotFound

from tgbot.models.sql_request import select_reward, select_photo, select_user
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


async def edit_message(message: Union[types.Message, types.CallbackQuery], text=None, markup=None, photo=None, video=None):
    if isinstance(message, types.CallbackQuery):
        message = message.message

    if photo:
        # если есть фото, изменяем сообщение с фото
        media = InputMedia(media=photo)
        if message.photo:
            try:
                await message.edit_media( media=media )
                await message.edit_caption( caption=text, reply_markup=markup)
            except MessageCantBeEdited:
                await message.answer_photo(photo=photo, caption=text, reply_markup=markup)
        else:
            await message.delete()
            await message.answer_photo(photo=photo,caption=text, reply_markup=markup)
    elif video:
        # если есть видео, изменяем сообщение с видео
        # await message.edit_caption( caption=text, reply_markup=markup  )
        await message.delete()
        # media = InputMediaVideo(media=video)
        await message.answer_video( video=video,caption=text ,reply_markup=markup)
    else:
        # если нет ни фото, ни видео, изменяем сообщение без медиа
        try:
            if (not message.video) and (not message.video_note):
                await message.delete()
                await message.answer( text=text, reply_markup=markup )
            else:
                await message.delete()
                await message.answer(text=text, reply_markup=markup)
        except MessageCantBeEdited:
            await message.answer(text=text, reply_markup=markup)
        except BadRequest:
            logging.info(text)
            try:
                await message.edit_caption(caption=text, reply_markup=markup)
            except MessageToEditNotFound:
                await message.delete()
                await message.answer(text=text, reply_markup=markup)

async def profile_viewer(message:types.Message, text, photo=None, markup=None):
    if photo:
        # если есть фото, изменяем сообщение с фото
        if message.photo:
            media = InputMedia(media=photo)
            await message.edit_media( media=media )
            await message.edit_caption( caption=text, reply_markup=markup)
        else:
            media = InputMedia(media=photo)
            await message.delete()
            await message.answer_photo(photo=photo, caption=text, reply_markup=markup)
    elif photo is None:
        if message.photo:
            await message.delete()
            await message.answer(text=text, reply_markup=markup)
        else:
            try:
                await message.edit_text(text=text, reply_markup=markup)
            except MessageCantBeEdited as e:
                await message.delete()
                await message.answer( text=text, reply_markup=markup )
            except BadRequest as b:
                await message.delete()
                await message.answer( text=text, reply_markup=markup )
    else:
        logging.info(msg='------------Else---------------')



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
    name = anket['first_name']
    age = calculateAge( anket['birthday'] )
    coutry = anket['country']
    city = anket['town']
    confession = anket['confession']
    last_time = anket['last_time']
    user_info = await select_user(session=session, user_id=user_id_anket)
    guarantor = user_info[0]['guarantor']
    moderation = user_info[0]['moderation']
    text=''
    if type_profile =='favorites_profile':
        text = f'Вы смотрите анкеты понравившиеся вам\n\n'
    elif type_profile == 'interested_me':
        text = f'Вы смотрите анкеты которым понравились вы\n\n'
    elif type_profile == 'mutual_interest':
        text = f'Вы смотрите анкеты взаимного интереса\n\n'
    elif type_profile == 'not_interested_me':
        text = f'Вы смотрите анкеты не понравившиеся вам\n\n'
    if moderation == True:
        text += f'✅'
    if guarantor is not None:
        text += f'📮'
    reward_db = await select_reward(session=session, user_id=user_id_anket)
    # ели есть награды в БД
    if len(reward_db) > 0:
        # удаление награды
        if return_reward:
            for rew in reward_db:
                if rew['reward'] == reward:
                    continue
                else:
                    text += f'{rew["reward"]}'
        # добавление награды
        else:
            for rew in reward_db:
                text += f'{rew["reward"]}'
            if reward is not None:
                text += f'{reward}'
        text += '\n'
    # если нет награды в БД
    elif reward is not None:
        text += f'{reward}\n'
    text += f'{name}, {age}\n'
    text += f'{coutry}, {city}\n'
    text += f'{confession}\n'
    correct_date = last_time.strftime("%d-%m-%Y")
    text += f'Дата последнего посещения: {correct_date}'
    text += f'\n\nНомер анкеты: {user_id_anket}'
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



