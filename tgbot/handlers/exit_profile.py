import logging
from typing import Union

from aiogram import types, Dispatcher

from tgbot.keyboards.inline import exit_profile_kb, exit_profile_cd, exit_keyboard_confirm, exit_confirm_keyboard_cd, \
    confirm_restore_account_kb, confirm_restore_account_cd
from tgbot.keyboards.reply import main_menu_kb
from tgbot.models.sql_request import update_user_info, select_user
from tgbot.services.auxiliary_functions import edit_message


async def hide_show_profile(message:Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.Message):
        user_id = message.chat.id
    elif isinstance(message, types.CallbackQuery):
        user_id = message.message.chat.id
    session = message.bot.data['session_maker']
    user_info = await select_user(session=session, user_id=user_id)
    status_user = user_info[0]['status']
    if status_user == 'user':
        text = '''
Для того, чтобы не удалять свою анкету, вы можете скрыть ее, при этом анкета не будет появляться у других пользователей в выдаче. 
Но вы так же можете просматривать и лайкать анкеты других участников'''
    elif status_user == 'hidden_user':
        text = '''
Ваша анкета скрыта, нажмите "Сделать видимой" и ваша анкета появится в выдаче другим пользователям'''
    else:
        text = 'Что-то пошло не так'
        kb = await main_menu_kb()
        await edit_message(message=message, text=text, markup=kb)
        return
    kb = await exit_profile_kb(user_id=user_id, status_user = status_user)
    await edit_message(message=message, text=text, markup=kb )

async def hide_show_profile_process(callback:types.CallbackQuery, callback_data:dict):
    logging.info("Hide profile process")
    call = callback_data['callback']
    user_id = callback.message.chat.id
    session = callback.bot.data['session_maker']
    if call == 'hide_profile':
        await update_user_info(session=session, user_id=user_id, status='hidden_user')
        text = 'Ваш профиль скрыт'
        await edit_message(message=callback, text=text)
    elif call == 'make_visible':
        text = 'Ваш профиль снова показывается'
        await update_user_info( session=session, user_id=user_id, status='user' )
        await edit_message( message=callback, text=text )

    else:
        pass



def exit_profile_handler(dp:Dispatcher):
    dp.register_message_handler( hide_show_profile, text='Скрыть/показать анкету', is_user=True )
    dp.register_callback_query_handler(hide_show_profile_process, exit_profile_cd.filter())

