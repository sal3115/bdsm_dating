import os
from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from tgbot.handlers.moderation import verification, complaints_moderation, reward_id, cancel_func, \
     mailing_users, mailing_kb_func, search_user_id_telegram, search_user_id_telegram_func, \
    no_verification
from tgbot.keyboards.inline import cancel_reward_cd, cancel_inline_kb, appoint_moderator_confirm_kb, \
    appoint_moderator_confirm_cd, cancel_cd, cancel_return_reward_cd
from tgbot.keyboards.reply import moderation_main_menu_kb
from tgbot.misc.states import RewardUser, AppointRemoveModerator, UserModeraion
from tgbot.models.sql_request import  select_user, update_user_info, \
    download_database, select_first_photo
from tgbot.services.auxiliary_functions import edit_message, format_text_profile


async def admin_menu(message:Union[types.Message, types.CallbackQuery]):
    text = 'Это панель администратора'
    kb = await moderation_main_menu_kb(admin_kb=True)
    await edit_message( message=message, text=text, markup=kb )


# async def reward_complete(call:types.CallbackQuery, callback_data:dict=None,state:FSMContext=None):
#     callback = callback_data['callback']
#     if callback == 'confirm':
#         data = await state.get_data()
#         id_user_reward = data['id_user_reward']
#         reward = data['self_reward']
#         session = call.bot.data['session_maker']
#         await insert_user_awards(session=session, user_id=id_user_reward, reward=reward)
#         await call.answer('Награда установлена')
#         await admin_menu(message=call)
#         await state.finish()
#     elif callback == 'wrong':
#         await call.answer('Награда отменена')
#         await state.finish()
#         await admin_menu(message=call)

# async def return_reward_complete(call:types.CallbackQuery, callback_data:dict=None,state:FSMContext=None):
#     callback = callback_data['callback']
#     if callback == 'confirm':
#         data = await state.get_data()
#         id_user_reward = data['id_user_reward']
#         reward = data['self_reward']
#         session = call.bot.data['session_maker']
#         await delete_reward(session=session, user_id=id_user_reward, reward=reward)
#         await call.answer('Награда удалена')
#         await admin_menu(message=call)
#         await state.finish()
#     elif callback == 'wrong':
#         await call.answer('Награда оставлена')
#         await state.finish()
#         await admin_menu(message=call)

#Назначить модератора
async def appoint_moderator(message:types.Message):
    text = 'Отправьте ИД пользователя, которого хотите назначить модератором'
    kb = await cancel_inline_kb()
    await edit_message(message=message, text=text, markup=kb)
    await AppointRemoveModerator.appoint_id_state.set()

async def appoint_moderator_confirm(message:types.Message, state:FSMContext):
    session = message.bot.data['session_maker']
    try:
        user_id_appoint = int(message.text)
    except ValueError as e:
        text = 'Не правильный ИД'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        return
    user_appoint = await select_user(session=session, user_id=user_id_appoint)
    if user_appoint:
        first_photo_all = await select_first_photo(session=session, user_id=user_id_appoint)
        text, _ = await format_text_profile(user_appoint[0], session=session)
        kb = await appoint_moderator_confirm_kb(user_id=user_id_appoint)
        if len(first_photo_all) > 0:
            first_photo = first_photo_all[0]['photo_id']
            await edit_message(message=message, text=text, markup=kb, photo=first_photo)
        else:
            await edit_message(message=message, text=text, markup=kb)

        await AppointRemoveModerator.appoint_confirm_state.set()
    else:
        text = 'Не правильный ИД'
        kb = await cancel_inline_kb()
        await edit_message(message=message, text=text, markup=kb)
        return

async def appoint_moderator_complete(call:types.CallbackQuery, callback_data:dict, state:FSMContext):
    callback = callback_data['callback']
    user_id_moderator = int(callback_data['user_id'])
    session = call.bot.data['session_maker']
    if callback == 'confirm':
        await update_user_info(session=session, user_id=user_id_moderator, status = 'moderator')
        await call.answer(f'Юзер с номером ИД {user_id_moderator} назначен модератором')
        text = 'Вы назначены модератором'
        kb = await moderation_main_menu_kb()
        await call.bot.send_message(chat_id=user_id_moderator, text=text, reply_markup=kb)
        await admin_menu(message=call)
        await state.finish()
    elif callback == 'wrong':
        await call.answer('Назначение модератора отменено')
        await admin_menu(message=call)
        await state.finish()



#Убрать модератора
async def remove_moderator(message:types.Message):
    text = 'Отправьте ИД пользователя, которого хотите убрать из модераторов'
    kb = await cancel_inline_kb()
    await edit_message(message=message, text=text, markup=kb)
    await AppointRemoveModerator.remove_id_state.set()


async def remove_moderator_confirm(message:types.Message, state:FSMContext=None):
    session = message.bot.data['session_maker']
    try:
        user_id_appoint = int(message.text)
    except ValueError:
        text = 'Отправьте ИД пользователя, которого хотите убрать из модераторов'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        return
    user_appoint = await select_user(session=session, user_id=user_id_appoint)
    if user_appoint:
        first_photo = await select_first_photo(session=session, user_id=user_id_appoint)
        text, _ = await format_text_profile(user_appoint[0], session=session)
        kb = await appoint_moderator_confirm_kb(user_id=user_id_appoint)
        await edit_message(message=message, text=text, markup=kb, photo=first_photo)
        await AppointRemoveModerator.remove_confirm_state.set()
    else:
        text = 'Не правильный ИД'
        await edit_message(message=message, text=text)
        return


async def remove_moderator_complete(call:types.CallbackQuery, callback_data:dict, state:FSMContext):
    callback = callback_data['callback']
    user_id_moderator = int(callback_data['user_id'])
    session = call.bot.data['session_maker']
    if callback == 'confirm':
        await update_user_info(session=session, user_id=user_id_moderator, status = 'user')
        await call.answer(f'Юзера с номером ИД {user_id_moderator} убрали с модераторов')
        await admin_menu(message=call)
        await state.finish()
    elif callback == 'wrong':
        await call.answer('Юзер оставлен модератором')
        await admin_menu(message=call)
        await state.finish()


#Скачать БД
async def download_db(message:types.Message):
    session = message.bot.data['session_maker']
    await download_database(session=session)
    directory = f"save_db/"
    for filename in os.listdir( directory ):
        file_path = os.path.join( directory, filename )
        with open( file_path, "rb" ) as file:
            await message.answer_document( file )



async def restart_state(message:types.Message, state:FSMContext):
    await state.reset_state()
    await message.answer("Произведен сброс, нажмите команду /start, чтобы начать сначала")
def administrator_handler(dp:Dispatcher):
    dp.register_message_handler(restart_state, commands='restart', state='*')

    dp.register_message_handler(admin_menu,commands='start' ,is_admin=True)
    dp.register_message_handler(no_verification,state=UserModeraion.no_verification_state,is_admin = True )
    dp.register_message_handler( verification, text='Верификация', is_admin=True )
    # жалобы
    dp.register_message_handler( complaints_moderation, text='Жалобы', is_admin=True )
    # # награды
    dp.register_message_handler( reward_id, text='Наградить', is_admin=True )
    # dp.register_callback_query_handler( reward_complete, cancel_reward_cd.filter(),
    #                                     state=RewardUser.reward_confirm_state, is_admin=True )
    # забрать награду
    # dp.register_message_handler( return_reward_id, text='Забрать награду', is_admin=True )
    # dp.register_callback_query_handler( return_reward_complete, cancel_return_reward_cd.filter(),
    #                                     state=RewardUser.return_reward_confirm_state, is_admin=True )
    # Назначить модератора
    dp.register_message_handler(appoint_moderator,text='Назначить модератора', is_admin=True)
    dp.register_message_handler(appoint_moderator_confirm, state=AppointRemoveModerator.appoint_id_state)
    dp.register_callback_query_handler(cancel_func, cancel_cd.filter(), state=AppointRemoveModerator.appoint_id_state)
    dp.register_callback_query_handler(appoint_moderator_complete, appoint_moderator_confirm_cd.filter(), state=AppointRemoveModerator.appoint_confirm_state)

    # Убрать модератора
    dp.register_message_handler(remove_moderator,text='Убрать модератора', is_admin=True)
    dp.register_callback_query_handler(cancel_func, cancel_cd.filter(), state=AppointRemoveModerator.remove_id_state)
    dp.register_message_handler(remove_moderator_confirm, state=AppointRemoveModerator.remove_id_state)
    dp.register_callback_query_handler(remove_moderator_complete, appoint_moderator_confirm_cd.filter(), state=AppointRemoveModerator.remove_confirm_state)

    # Скачать БД
    dp.register_message_handler(download_db,text='Скачать БД', is_admin=True)

    #разные ссылки
    # dp.register_message_handler(different_link_mod, text='Разные ссылки', is_admin=True)
    #Рекомендации
    dp.register_message_handler(search_user_id_telegram, text='Поиск по ID телеграм', is_admin=True)
    dp.register_callback_query_handler( search_user_id_telegram_func, text='search_for_id', is_admin=True )
    #Рассылка
    dp.register_message_handler(mailing_users, text='Рассылка', is_admin=True)
    dp.register_callback_query_handler(mailing_kb_func, text='make_newsletter', is_admin=True)



