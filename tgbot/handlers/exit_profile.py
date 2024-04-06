from typing import Union

from aiogram import types, Dispatcher

from tgbot.keyboards.inline import exit_profile_kb, exit_profile_cd, exit_keyboard_confirm, exit_confirm_keyboard_cd, \
    confirm_restore_account_kb, confirm_restore_account_cd
from tgbot.keyboards.reply import main_menu_kb
from tgbot.models.sql_request import update_user_info, select_user
from tgbot.services.auxiliary_functions import edit_message


async def exit_profile(message:Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.Message):
        user_id = message.chat.id
    elif isinstance(message, types.CallbackQuery):
        user_id = message.message.chat.id
    session = message.bot.data['session_maker']
    user_info = await select_user(session=session, user_id=user_id)
    status_user = user_info[0]['status']
    if status_user == 'user':
        text = '''
Вы можете на время скрыть свою анкету, удалить анкету полностью, но пользоваться
полезными материалами или выйти из сервиса полностью (оплата за текущий период
не будет возвращена)'''
    elif status_user == 'hidden_user':
        text = '''
        Ваша анкета скрыта от других пользоаптелей вы можете сделать её видимой, удалить анкету полностью, но пользоваться
полезными материалами или выйти из сервиса полностью (оплата за текущий период не будет возвращена)'''
    else:
        text = 'Что-то пошло не так'
        kb = await main_menu_kb()
        await edit_message(message=message, text=text, markup=kb)
        return
    kb = await exit_profile_kb(user_id=user_id, status_user = status_user)
    await edit_message(message=message, text=text, markup=kb )

#функция для скрытия анкеты
async def hide_profile_func(call:types.CallbackQuery):
    user_id = call.from_user.id
    session = call.bot.data['session_maker']
    await update_user_info(session=session, user_id=user_id, status='hidden_user')
    text = 'Теперь ваш аккаунт скрыт от других пользователей'
    kb = await main_menu_kb()
    await edit_message(message=call, text=text, markup=kb)

#функция для показа анкеты
async def make_visible_func(call:types.CallbackQuery):
    user_id = call.from_user.id
    session = call.bot.data['session_maker']
    await update_user_info(session=session, user_id=user_id, status='user')
    text = 'Теперь ваш аккаунт видим других пользователей'
    kb = await main_menu_kb()
    await edit_message(message=call, text=text, markup=kb)

#функция для выхода из профиля
async def exit_profile_func(call:types.CallbackQuery):
    session = call.bot.data['session_maker']
    user_id = call.from_user.id
    await update_user_info( session=session, user_id=user_id, status='exit_user' )
    text = 'Вы вышли из аккаунта вам доступны только полезные материалы и вы так же всегда можете восстановить аккаунт'
    kb = await main_menu_kb(status_user='exit_user')
    await edit_message(message=call, text=text, markup=kb)


#функция для удаление профиля
async def delete_profile_func(call:types.CallbackQuery):
    session = call.bot.data['session_maker']
    user_id = call.from_user.id
    await update_user_info( session=session, user_id=user_id, status='delete_user' )
    text = 'Вы удалили аккаунта, но вы всегда можете восстановить аккаунт'
    kb = await main_menu_kb(status_user='delete_user')
    await edit_message(message=call, text=text, markup=kb)



#принимаем callback от инлайнт клавы exit_profile_kb
async def exit_profile_inlin_func(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    if callback == 'hide_profile':
        text = 'вы действительно хотите скрыть свою анкету'
        kb = await exit_keyboard_confirm(status_user='hide_profile')
        await edit_message(message=call, text = text, markup=kb)
    elif callback == 'delete_profile':
        text = 'вы действительно хотите удалить свою анкету'
        kb = await exit_keyboard_confirm(status_user='delete_profile')
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'exit_profile':
        text = 'вы действительно хотите выйти из сервиса, при этом вы сможете пользоваться полезными сервисами'
        kb = await exit_keyboard_confirm(status_user='exit_profile')
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'make_visible':
        text = 'вы действительно хотите свою анкету видимой'
        kb = await exit_keyboard_confirm(status_user='make_visible')
        await edit_message(message=call, text=text, markup=kb)
    else:
        text = 'Что-то пошло не так'
        await call.message.answer(text=text)

#обработка кнопки подтверждения
async def confirm_exit(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    status_user = callback_data['status_user']
    if callback == 'confirm':
        if status_user == 'hide_profile':
            await hide_profile_func(call=call)
        elif status_user == 'delete_profile':
            await delete_profile_func(call = call)
        elif status_user == 'exit_profile':
            await exit_profile_func(call=call)
        elif status_user == 'make_visible':
            await make_visible_func(call = call)
    elif callback == 'cancel':
        await exit_profile(message=call)


async def restore_account(message:types.Message):
    text = "Вы действительно хотите воcстановить аккаунт?"
    kb = await confirm_restore_account_kb()
    await edit_message(message=message, text=text, markup=kb)



async def confirm_restore_account(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id = call.message.chat.id
    if callback == 'yes':
        session = call.bot.data['session_maker']
        await update_user_info(session=session, user_id=user_id, status='user')
        text = 'Вы восстановили свой аккаунт'
        kb = await main_menu_kb()
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'no':
        text = 'Вы отменили восстановления аккаунта'
        await edit_message(message=call, text=text)


def exit_profile_handler(dp:Dispatcher):
    dp.register_message_handler( exit_profile, text='❌Выйти из сервиса', is_user=True )
    dp.register_callback_query_handler(exit_profile_inlin_func, exit_profile_cd.filter())
    dp.register_callback_query_handler(confirm_exit, exit_confirm_keyboard_cd.filter())
    #Обработка восстановления аккаунта
    dp.register_message_handler(restore_account, text = 'Восстановить аккаунт',is_user_exit = True)
    dp.register_message_handler(restore_account, text = 'Восстановить аккаунт',is_user_delete = True)

    dp.register_callback_query_handler(confirm_restore_account, confirm_restore_account_cd.filter())
    dp.register_message_handler( exit_profile, text='❌Выйти из сервиса', is_user_exit=True )
