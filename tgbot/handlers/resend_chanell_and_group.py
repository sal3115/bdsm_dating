import logging
from asyncio import sleep
from typing import Union

from aiogram import Dispatcher, types
from aiogram.types import InputFile

from tgbot.keyboards.inline import test_keyboard, test_keyboard_cd, resend_group_keyboard
from tgbot.models.sql_request import select_placement_group_channel_one, select_user, select_first_photo, \
    select_placement_group_channel, select_resend_free_platform, select_resend_platform_one, update_resend_free_platform
from tgbot.services.auxiliary_functions import format_text_profile

async def resend_group(message: types.Message, id_user, type_profile, ):
    session = message.bot.data['session_maker']
    profile = await select_user(session=session, user_id=id_user)
    if len(profile)<=0:
        return
    group_info = await select_placement_group_channel_one(session=session)
    for info in group_info:
        if type_profile == 'down':
            if info['title_thread'] == 'down':
                id_group = info['id_channel_group']
                message_thread_id = info['thread_message_id']
            else:
                continue
        elif type_profile == 'up':
            if info['title_thread'] == 'up':
                id_group = info['id_channel_group']
                message_thread_id = info['thread_message_id']
            else:
                continue
        else:
            return
        first_photo = await select_first_photo(session=session, user_id=id_user)
        text, user_id_anket = await format_text_profile( anket=profile[0], session=session )
        if len(first_photo) > 0:
            photo = first_photo[0]['photo_id']
        else:
            photo = InputFile('tgbot/misc/no_photo.jpg')
        get_me = await message.bot.get_me()
        user_name_bot = get_me.username
        text+= '\n' \
               f'Связь: https://t.me/{user_name_bot}?start=profile={profile[0]["id"]}'
        message_info = await message.bot.send_photo( chat_id=id_group, caption=text, photo=photo,
                                                  message_thread_id=message_thread_id if message_thread_id is not None else None)
        logging.info( message_info )



async def resend_group_free(message: Union[types.Message, types.CallbackQuery], id_user):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    session = message.bot.data['session_maker']
    profile = await select_user(session=session, user_id=id_user)
    free_platforms = await select_resend_free_platform(session=session, user_id=id_user)
    logging.info(free_platforms)
    if len(profile)<=0:
        return
    if len(free_platforms)<=0:
        return
    for all_info_group in free_platforms:
        message_id_group = all_info_group['message_id']
        if message_id_group is not None:
            return
        logging.info(all_info_group)
        search_partner_position = profile[0]['partner_position']
        id_mini_group = all_info_group['id_platform']
        group_info = await select_resend_platform_one(session=session,id_mini= id_mini_group, partner_position=search_partner_position)
        logging.info( group_info )
        if len(group_info) <=0:
            return
        id_group = group_info[0]['id_channel_group']
        logging.info(group_info[0])
        logging.info('thread_message_id' in group_info[0])
        if 'thread_message_id' in group_info[0]:
            message_thread_id = group_info[0]['thread_message_id']
        else:
            message_thread_id = None
        first_photo = await select_first_photo(session=session, user_id=id_user)
        text, user_id_anket = await format_text_profile( anket=profile[0], session=session )
        if len(first_photo) > 0:
            photo = first_photo[0]['photo_id']
        else:
            photo = InputFile('tgbot/misc/no_photo.jpg')
        get_me = await message.bot.get_me()
        user_name_bot = get_me.username
        anonymous = all_info_group['anonymous']
        text+= '\n' \
               f'Связь: <a href="https://t.me/{user_name_bot}?start=profile={profile[0]["id"]}">Анкета</a>'
        if anonymous is False:
            user_info = await message.bot.get_chat(chat_id=id_user)
            user_name_profile = user_info.username
            text+= f'\n' \
                   f'Личка: @{user_name_profile} '
        message_info = await message.bot.send_photo( chat_id=id_group, caption=text, photo=photo,
                                                  message_thread_id=message_thread_id)
        await update_resend_free_platform(session=session, user_id=id_user, mini_platform_id=id_mini_group, message_id=message_info.message_id)
        logging.info( message_info )



