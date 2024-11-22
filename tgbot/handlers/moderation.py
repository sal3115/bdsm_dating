import asyncio
import datetime
import logging
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked

from tgbot.handlers.main_menu import scrolling_photo_func
from tgbot.keyboards.inline import verify_user_kb, verify_user_cd, \
    scrolling_photos_moderation_cd, cancel_inline_kb, cancel_cd, complaints_kb, complaints_cd, complaints_profile_kb, \
    complaints_profile_cd, scrolling_photos_complains_cd, cancel_reward_inline_kb, cancel_reward_cd, \
    different_link_mod_kb, different_link_CD, different_link_edit_descr_or_link, different_link_edit_descr_or_link_CD, \
    recommendation_search_kb, mailing_kb, search_user_kb, scrolling_photos_search_cd, appoint_guarantor_confirm_kb, \
    appoint_guarantor_confirm_cd, cancel_return_reward_cd, edit_user_moderation_kb, edit_user_moderation_cb
from tgbot.keyboards.reply import moderation_main_menu_kb
from tgbot.misc.states import UserModeraion, RewardUser, EditLink, NewLink, RecommendationsState, MailingState, \
    SearchUser, BlockUser, EditUserModeration
from tgbot.models.sql_request import select_moderation_user_id, select_user, select_user_anketa_verefication, \
    select_first_photo, update_moderation, update_user_info, select_complaints, select_complaints_join, \
    update_complaint_decision, select_column_data, select_user_anketa, select_all_users_mailing, insert_rejecting_verification, \
    select_rejection_user, delete_rejecting_verification, insert_block_user_description, select_block_user_description, \
    delete_block_user_description
from tgbot.services.auxiliary_functions import edit_message, format_text_profile


async def text_verify_user(user=None, user_id = None, session=None, type_profile = None):
    status_all = {'user':'Пользователь', 'hidden_user':'Скрытый пользователь', 'delete_user':'Удаленный пользователь',
                  'exit_user':'Пользователь вышел', 'moderator':'Модератор','admin':'Администратор','block_user':'Заблокированый пользователь',
                  'no_ver_user': 'Пользователь с отклоненной верификацией'}

    text =''
    if user_id:
        user = await select_user(session=session, user_id=user_id)
        user = user[0]
    else:
        user=user
    user_id = user_id if user_id else user['user_id']
    time_reg = user['time_reg']
    correct_time_reg = time_reg.strftime( "%d-%m-%Y" )
    date_birthday = user['birthday']
    correct_date_birthday = date_birthday.strftime( "%d-%m-%Y" )
    rejection_verification = await select_rejection_user(session=session, user_id=user_id)
    block_user_description = await select_block_user_description(session=session, user_id=user_id)
    reward_user = ''
    if type_profile is None:
        text += f"Новый пользователь:\n"
    elif type_profile == 'search_user':
        text = 'Найден пользователь:\n'
    text += f"user_id: {user['user_id']} \n" \
    f"Статус: {status_all[user['status']]} \n" \
    f"Модерация: {'✅' if user['moderation'] else 'нет'} \n" \
    f"Имя: {user['first_name']}\n" \
    f"User_name: {user['username']}\n" \
    f"Пол: {'женский' if user['gender']=='women' else 'мужской'}\n" \
    f"Дата рождения: {correct_date_birthday}\n" \
    f"Город проживания: {user['city']}\n" \
    f"Партнер из другого города: {'Да' if user['partner_another_city'] else 'Нет'}\n" \
    f"Минимальный возраст: {user['min_age']}\n" \
    f"Максимальный возраст: {user['max_age']}\n" \
    f"Дата регистрации :{correct_time_reg}\n"
    if len(rejection_verification) > 0:
        text += f'Причина отклонения верификации: {rejection_verification[0]["description"]}\n'
    if len(block_user_description) > 0:
        text += f'Причина блокировка пользователя: {block_user_description[0]["description"]}\n'
    return text


# Первая страница модератора
async def verify_user(message:Union[types.Message, types.CallbackQuery]):
    text = 'Это страница модераторов'
    logging.info( f'---------{message}--------------' )
    kb = await moderation_main_menu_kb()
    await edit_message(message=message, text=text, markup=kb)

# Верификация
async def verification(message:Union [types.Message, types.CallbackQuery], page = 0):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    session = message.bot.data['session_maker']
    users = await select_user_anketa_verefication(session=session)
    logging.info(len(users))
    logging.info(page)

    if len(users) == 0:
        await edit_message(message=message, text='анкет нет')
        return
    if page+1 > len(users):
        page = 0
    user_profile = users[0+page]
    photos = await select_first_photo( session=session, user_id=user_profile['user_id'] )
    text = await text_verify_user(user=user_profile, session=session)
    kb = await verify_user_kb(user_id=user_profile['user_id'], page=page)
    if len(photos)<1:
        await message.delete()
        await edit_message(message=message, text=text, markup=kb)
    elif len(photos) > 0:
        await message.delete()
        if len(text) > 1024:
            new_text = text.split('Дата регистрации')
            await message.answer_photo(photo=photos[0]['photo_id'],caption=new_text[0])
            await edit_message(message=message, text=f'Дата регистрации{new_text[1]}', markup=kb)
        else:
            await edit_message(message=message, photo=photos[0]['photo_id'],text=text, markup=kb)


#Фото
async def scrolling_photo_moderation_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page, type_profiles='moderation_profile')
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page, type_profiles='moderation_profile')
    elif callback == 'back':
        await verification(message=call, page=page)
    await call.answer()

#State no_verification
async def no_verification(message:types.Message, state:FSMContext):
    logging.info('no verification')
    answer_moderation = message.text
    if answer_moderation == 'Верификация' or answer_moderation == 'Жалобы' or answer_moderation == 'Наградить' or answer_moderation == 'Забрать награду':
        await message.delete()
        return
    data = await state.get_data()
    type_profile = data['type_profile']
    user_id = data['user_id']
    page = data['page']
    session = message.bot.data['session_maker']
    check_rejection = await select_rejection_user(session=session, user_id=user_id)
    if len(check_rejection) > 0:
        await delete_rejecting_verification(session=session, user_id=user_id)
    await insert_rejecting_verification(session=session, user_id=user_id, description=answer_moderation)
    await update_user_info(session=session, user_id=user_id, status = 'no_ver_user')
    try:
        await message.bot.send_message(chat_id=user_id, text=answer_moderation)
    except BotBlocked:
        info_user = await select_user(session=session, user_id=user_id)
        status = info_user[0]['status']
        if status !='block_user':
            await update_user_info(session=session, user_id=user_id, status='exit_user')
        else:
            pass
        await message.answer( text=f'Пользователю с ид {user_id} заблокировал бота' )
    except:
        pass
    finally:
        await state.finish()
        if type_profile == 0 or type_profile == '0':
            await verification( message=message, page=page + 1 )
        elif type_profile == 'search_user':
            pass
        else:
            logging.info(write_moderation)
            logging.info(data)

#State write
async def write_moderation(message:types.Message, state:FSMContext):
    answer_moderation = message.text
    if answer_moderation == 'Верификация' or answer_moderation == 'Жалобы' or answer_moderation == 'Наградить' or answer_moderation == 'Забрать награду':
        await message.delete()
        return
    data = await state.get_data()
    logging.info(data)
    type_profile = data['type_profile']
    user_id = data['user_id']
    page = data['page']
    try:
        await message.bot.send_message(chat_id=user_id, text=answer_moderation)
        await message.answer(text=f'Пользователю с ид {user_id} отправлено сообщение: \n\n'
                              f'{answer_moderation}')
    except BotBlocked:
        session = message.bot.data['session_maker']
        info_user = await select_user(session=session, user_id=user_id)
        status = info_user[0]['status']
        if status != 'block_user':
            await update_user_info(session=session, user_id=user_id, status = 'exit_user')
        else:
            pass
        await message.answer( text=f'Пользователю с ид {user_id} заблокировал бота' )
    except:
        pass
    finally:
        await state.finish()
        if type_profile == 0 or type_profile=='0':
            await verification(message=message, page=page+1)
        elif type_profile == 'search_user':
            pass
        else:
            logging.info(write_moderation)
            logging.info(data)

#Callbback главного меню
async def verify_kb(call: types.CallbackQuery, callback_data:dict, counter=0, state:FSMContext=None):
    callback = callback_data['callback']
    user_id_profile = callback_data['user_id']
    page = int(callback_data['page'])
    type_profile = callback_data['tp']
    session = call.bot.data['session_maker']
    if callback == 'photo':
        if type_profile == 0 or type_profile=='0':
            await scrolling_photo_func(call = call, user_id_anket=user_id_profile, counter=counter, page=page, type_profiles='moderation_profile')
        elif type_profile == 'search_user':
            await scrolling_photo_func(call = call, user_id_anket=user_id_profile, counter=counter, page=page, type_profiles='search_user')
    elif callback == 'video':
        profile_user = await select_user(session=session, user_id=user_id_profile)
        video = profile_user[0]['video']
        if video is None:
            await call.answer( 'У пользователя нет видеовизитки' )
        else:
            if type_profile == 0 or type_profile == '0':
                kb = await verify_user_kb( user_id=user_id_profile, page=page, call_back=callback )
                await edit_message( message=call, video=video, markup=kb )
            elif type_profile == 'search_user':
                kb = await verify_user_kb( user_id=user_id_profile, page=page, type_profile='search_user', call_back=callback )
                await edit_message( message=call, video=video, markup=kb )
    elif callback == 'about_me':
        profile_user = await select_user( session=session, user_id=user_id_profile )
        about_me = profile_user[0]['about_my_self']
        if type_profile == 0 or type_profile=='0':
            kb = await verify_user_kb( user_id=user_id_profile, page=page, call_back=callback )
            await edit_message( message=call, text=about_me, markup=kb )
        elif type_profile == 'search_user':
            kb = await verify_user_kb( user_id=user_id_profile, page=page, type_profile='search_user', call_back=callback, all_info_user=profile_user[0] )
            await edit_message( message=call, text=about_me, markup=kb )
    elif callback == 'verify':
        profile_user = await select_user( session=session, user_id=user_id_profile )
        if profile_user[0]['status'] == 'block_user':
            await update_user_info( session=session, user_id=user_id_profile, moderation=True,
                                    time_verif=datetime.datetime.now().date(), status='block_user' )
        else:
            await update_user_info(session=session, user_id=user_id_profile, moderation=True, time_verif=datetime.datetime.now().date(), status='user' )
        check_rejecttion = await select_rejection_user(session=session, user_id=user_id_profile)
        if len(check_rejecttion) > 0:
            await delete_rejecting_verification(session=session, user_id=user_id_profile)
        await call.answer("Пользователь верифицирован")
        if type_profile == 0 or type_profile=='0':
            await verification(message=call, page = page+1)
        elif type_profile == 'search_user':
            await search_user_id_telegram_state(message=call, user_id=user_id_profile)
    elif callback == 'no_verify':
        await call.message.answer('Напиши причину отказа в модерации', reply_markup=await cancel_inline_kb(user_id=user_id_profile, page=page))
        await UserModeraion.no_verification_state.set()
        await state.update_data(user_id=user_id_profile, page=page, type_profile=type_profile )
    elif callback == 'next_profile':
        await verification(message=call, page = page+1)
    elif callback == 'write':
        await call.message.answer( 'Напиши текст сообщения',
                                   reply_markup=await cancel_inline_kb( user_id=user_id_profile, page=page ) )
        await UserModeraion.write_state.set()
        await state.update_data( user_id=user_id_profile, page=page, type_profile=type_profile )
    elif callback == 'unlock':
        all_user_info = await select_user(session=session, user_id=user_id_profile)
        user_info = all_user_info[0]
        status = user_info['status']
        if status == 'block_user':
            check_block_description = await select_block_user_description( session=session, user_id=user_id_profile )
            check_rejection_description = await select_rejection_user( session=session, user_id=user_id_profile )
            if len( check_block_description ) > 0:
                await delete_block_user_description( session=session, user_id=user_id_profile )
            if len( check_rejection_description ) > 0:
                await update_user_info( session=session, user_id=user_id_profile, status='ver_user' )
            else:
                await update_user_info(session=session, user_id=user_id_profile, status='user')
            text = 'Пользователь разблокирован'
            await edit_message(message=call, text=text)
        else:
            await call.answer(text='Данный пользователь не заблокирован')
    elif callback == 'lock':
        all_user_info = await select_user( session=session, user_id=user_id_profile )
        user_info = all_user_info[0]
        status = user_info['status']
        if status == 'block_user':
            await call.answer(text='Данный пользователь и так заблокирован')
        else:
            text = 'Напиши причину блокировки пользователя'
            kb = await cancel_inline_kb()
            await edit_message( message=call, text=text, markup=kb )
            await BlockUser.block_user_state.set()
            await state.update_data( user_id=user_id_profile, page=page, type_profile=type_profile )
    elif callback == 'confirm_garant':
        text = 'Вы уверены что хотите подтвердить наличие гаранта у данного пользователя'
        kb = await appoint_guarantor_confirm_kb(user_id=user_id_profile)
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'profile':
        if type_profile == 'search_user':
            await search_user_id_telegram_state(message=call, user_id=user_id_profile)
        else:
            await verification(message=call, page=page)
    elif callback == 'edit_user':
        await edit_user_moderation_func(message=call,user_id_profile=user_id_profile)
    else:
        await call.message.answer('Что-то пошло не так')
    await call.answer()


async def edit_user_moderation_func(message:Union[types.Message, types.CallbackQuery], user_id_profile):
    text = 'Здесь вы можете изменить данные пользователя'
    kb = await edit_user_moderation_kb( user_id_profile=user_id_profile )
    await edit_message(message=message, text=text, markup=kb)


async def edit_user_moderation_cb_func(call:types.CallbackQuery, callback_data:dict, state:FSMContext=None):
    callback = callback_data['callback']
    user_id_profile = callback_data['user_id_profile']
    kb = await cancel_inline_kb()
    if callback == 'edit_first_name':
        text = 'Напиши новое имя'
        await edit_message(message=call, text=text, markup=kb)
        await EditUserModeration.first_name_state.set()
        await state.update_data( user_id_profile=user_id_profile )
    elif callback =='edit_last_name':
        text = 'Напиши новую фамилию'
        await edit_message(message=call, text=text, markup=kb)
        await EditUserModeration.last_name_state.set()
        await state.update_data( user_id_profile=user_id_profile )
    elif callback =='back':
        await search_user_id_telegram_state(message=call, user_id=user_id_profile)
    else:
        text = 'Что-то пошло не так функция edit_user_moderation_cb_func, обратись к администратору сервиса'
        await edit_message( message=call, text=text )

async def edit_user_moderation_state(message:types.Message, state:FSMContext):
    current_state = await state.get_state()
    session = message.bot.data['session_maker']
    data_state = await state.get_data()
    user_id_profile = data_state['user_id_profile']
    if current_state == 'EditUserModeration:first_name_state':
        first_name = message.text
        await update_user_info(session=session, user_id=user_id_profile, first_name=first_name )
    elif current_state == 'EditUserModeration:last_name_state':
        last_name = message.text
        await update_user_info(session=session, user_id=user_id_profile, last_name=last_name )
    else:
        text = 'Что-то пошло не так функция edit_user_moderation_state, обратись к администратору сервиса'
        await edit_message(message=message, text=text)
    await state.finish()
    await search_user_id_telegram_state( message=message, user_id=user_id_profile )


async def block_user_state(message:types.Message, state:FSMContext):
    reason_for_blocking = message.text
    if len(reason_for_blocking) > 1001:
        text = f'Уменьши сообщение до 1000 знаков сейчас знаков: {len(reason_for_blocking)}'
        kb = cancel_inline_kb()
        await edit_message(message=message, text=text, markup=kb)
        await BlockUser.block_user_state.set()
    data_state = await state.get_data()
    user_id_profile = data_state['user_id']
    page = data_state['page']
    session = message.bot.data['session_maker']
    await update_user_info( session=session, user_id=user_id_profile, status='block_user' )
    await insert_block_user_description(session=session, user_id=user_id_profile, description=reason_for_blocking)
    text = 'Данный пользователь заблокирован'
    await edit_message(message=message, text=text)
    await state.finish()


async def cancel_func(call: types.CallbackQuery, state: FSMContext, callback_data:dict):
    logging.info('-------------cancel kb-------------')
    user_id = callback_data['user_id']
    page = int(callback_data['page'])
    await state.finish()
    await edit_message(message=call, text='Отмена')

#Жалобы
async def complaints_moderation(message:Union[types.Message, types.CallbackQuery], page=0):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    session = message.bot.data['session_maker']
    complaints_all = await select_complaints(session=session)
    logging.info(['-------------len complaints_all----------', len(complaints_all)])
    page = int(page)
    if len(complaints_all) == 0:
        text = 'Больше жалоб нет'
        kb = await moderation_main_menu_kb()
        await edit_message(message=message, text=text)
        return
    if int(page) +1 > len(complaints_all):
        page = 0
    logging.info(['-------------page complaints----------', page])
    complaints_one = complaints_all[0+page]
    logging.info(['-------------complaints_one----------', complaints_one])

    user_id = complaints_one['id_user']
    complaints_user_id = complaints_one['id_user_complaints']
    data_text = await select_complaints_join(session=session, user_id=user_id, complaints_user_id=complaints_user_id)
    text = f'Пользователь <a href="https://t.me/{data_text[0]["user_username"]}">{data_text[0]["user_first_name"]} {data_text[0]["user_last_name"]}</a>' \
           f' написал жалобу на пользователя <a href="https://t.me/{data_text[0]["complaints_user_username"]}">{data_text[0]["complaints_user_first_name"]} {data_text[0]["complaints_user_last_name"]}</a>' \
           f' с текстом:\n{data_text[0]["complaints"]}'
    kb = await complaints_kb(complaints_user_id=complaints_user_id, page=page)
    await edit_message(message=message, text=text, markup=kb)


async def complaints_kb_func(call: types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    complaints_user_id = callback_data['com_user_id']
    page = int(callback_data['page'])
    if callback == 'block_user':
        session = call.bot.data['session_maker']
        await update_user_info(session= session, user_id=complaints_user_id, status = 'block_user')
        await update_complaint_decision(session=session, complaint_user_id=complaints_user_id, decision=True)
        await call.answer('Пользователь заблокирован')
        await call.message.delete()
        await complaints_moderation(message=call, page=page+1)
    elif callback == 'reject':
        session = call.bot.data['session_maker']
        await update_complaint_decision(session=session, complaint_user_id=complaints_user_id, decision=True)
        await call.answer( 'Жалоба отклонена' )
        await call.message.delete()
        await complaints_moderation( message=call, page=page + 1 )
    elif callback == 'view_profile':
        session = call.bot.data['session_maker']
        first_photo_all = await select_first_photo(session=session, user_id=complaints_user_id)
        text = await text_verify_user(user_id=complaints_user_id, session=session)
        kb = await complaints_profile_kb( user_id=complaints_user_id, page=page, session=session )
        if len(first_photo_all) > 0:
            first_photo = first_photo_all[0]['photo_id']
            await edit_message( message=call, text=text, markup=kb, photo=first_photo )
        else:
            await edit_message(message=call, text=text, markup=kb)
    elif callback == 'next_complaint':
        await complaints_moderation(message=call, page=int(page)+1)
    await call.answer()


async def complaints_profile_func_cd(call:types.CallbackQuery, callback_data:dict=None, counter=0):
    callback = callback_data['callback']
    page = callback_data['page']
    user_id_complaint = callback_data['user_id']
    session = call.bot.data['session_maker']
    if callback == 'photo':
        await scrolling_photo_func( call=call, user_id_anket=user_id_complaint, counter=counter, page=page,
                                    type_profiles='complaints_profile' )
    elif callback == 'video':
        profile_user = await select_user( session=session, user_id=user_id_complaint )
        video = profile_user[0]['video']
        logging.info( f'---------video--------------' )
        logging.info( f'---------{video}--------------' )
        if video is None:
            await call.answer( 'У пользователя нет видеовизитки' )
        else:
            kb = await complaints_profile_kb( user_id=user_id_complaint, page=page, session=session )
            await edit_message( message=call, video=video, markup=kb )
    elif callback == 'about_me':
        profile_user = await select_user( session=session, user_id=user_id_complaint )
        about_me = profile_user[0]['about_my_self']
        kb = await complaints_profile_kb( user_id=user_id_complaint, page=page, session=session )
        await edit_message( message=call, text=about_me, markup=kb )
    elif callback == 'back':
        await complaints_moderation( message=call, page=page )


async def complaints_photo(call:types.CallbackQuery, callback_data:dict=None):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int( callback_data['counter'] )
    page = int( callback_data['page'] )
    if callback == 'previous_photo':
        await scrolling_photo_func( call=call, user_id_anket=user_id_anket, counter=counter - 1, page=page,
                                    type_profiles='complaints_profile' )
    elif callback == 'next_photo':
        await scrolling_photo_func( call=call, user_id_anket=user_id_anket, counter=counter + 1, page=page,
                                    type_profiles='complaints_profile' )
    elif callback == 'back':
        session = call.bot.data['session_maker']
        text = await text_verify_user( user_id=user_id_anket, session=session )
        kb = await complaints_profile_kb( user_id=user_id_anket, page=page, session=session )
        await edit_message( message=call, text=text, markup=kb )
    await call.answer()

#Награды
# просьба написать ИД
async def reward_id(message:types.Message):
    text = 'Напишите ID пользователя которого хотите наградить'
    kb= await cancel_inline_kb()
    await edit_message(message=message, text=text, markup=kb)
    await RewardUser.reward_id_state.set()

#Принимаем ИД просим награду dp.register_message_handler(reward_it_self, state=RewardUser.reward_id_state)
async def reward_self(message:types.Message, state:FSMContext=None):
    session = message.bot.data['session_maker']
    text ='Отправьте значок который хотите присвоить пользователю'
    kb = await cancel_inline_kb()
    id_user_reward = message.text
    check_user = await select_user(session=session, user_id=id_user_reward)
    if check_user:
        await state.update_data(id_user_reward = id_user_reward)
        await edit_message( message=message, text=text, markup=kb )
        await RewardUser.reward_state.set()
    else:
        text = 'Такого ID нет, попробуйте ввести снова или нажмите отмена'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        await RewardUser.reward_id_state.set()
#Принимем награду, спрашиваем точно ли хочет наградить этого пользователя  dp.message_handler(reward_confirm, state=RewardUser.reward_state)
async def reward_confirm(message:types.Message, state:FSMContext=None):
    session= message.bot['session_maker']
    data = await state.get_data()
    self_reward = message.text
    user_id_reward = data['id_user_reward']
    profile = await select_user( session=session, user_id=user_id_reward )
    first_photo_db = await select_first_photo( session=session, user_id=user_id_reward )
    text, _ = await format_text_profile(anket=profile[0], session=session, reward = self_reward)
    text += '\nВы уверены, что хотите наградить именно этого пользователя? Анкета выглядит корректно?'
    kb = await cancel_reward_inline_kb()
    await state.update_data( self_reward=self_reward )
    if len(first_photo_db) >0:
        first_photo = first_photo_db[0]['photo_id']
        await edit_message( message=message, text=text, markup=kb, photo=first_photo )
    elif len(first_photo_db) == 0:
        await edit_message( message=message, text=text, markup=kb)
    await RewardUser.reward_confirm_state.set()


#Принимаем подтверждение подтверждение dp.register_callback_query_handler(reward_complete, state=RewardUser.reward_confirm_state)
# async def reward_complete(call:types.CallbackQuery, callback_data:dict=None,state:FSMContext=None):
#     callback = callback_data['callback']
#     if callback == 'confirm':
#         data = await state.get_data()
#         id_user_reward = data['id_user_reward']
#         reward = data['self_reward']
#         session = call.bot.data['session_maker']
#         await insert_user_awards(session=session, user_id=id_user_reward, reward=reward)
#         await call.answer('Награда установлена')
#         await verify_user(message=call)
#         await state.finish()
#     elif callback == 'wrong':
#         await call.answer('Награда отменена')
#         await state.finish()
#         await verify_user(message=call)


#забрать награду
# async def return_reward_id(message:types.Message):
#     text = 'Напишите ID пользователя у которого хотите забрать награду'
#     kb= await cancel_inline_kb()
#     await edit_message(message=message, text=text, markup=kb)
#     await RewardUser.return_reward_id_state.set()

#Принимаем ИД просим награду которую хотим забрать dp.register_message_handler(return_reward_self, state=RewardUser.return_reward_id_state)
async def return_reward_self(message:types.Message, state:FSMContext=None):
    session = message.bot.data['session_maker']
    text ='Отправьте значок который хотите забрать у пользователю'
    kb = await cancel_inline_kb()
    id_user_reward = message.text
    check_user = await select_user(session=session, user_id=id_user_reward)
    if check_user:
        await state.update_data(id_user_reward = id_user_reward)
        await edit_message( message=message, text=text, markup=kb )
        await RewardUser.return_reward_state.set()
    else:
        text = 'Такого ID нет, попробуйте ввести снова или нажмите отмена'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        await RewardUser.return_reward_id_state.set()
#Принимем награду, спрашиваем точно ли хочет забрать награду у этого пользователя  dp.message_handler(return_reward_confirm, state=RewardUser.return_reward_state)
async def return_reward_confirm(message:types.Message, state:FSMContext=None):
    session= message.bot['session_maker']
    data = await state.get_data()
    self_reward = message.text
    user_id_reward = data['id_user_reward']
    profile = await select_user( session=session, user_id=user_id_reward )
    first_photo = await select_first_photo( session=session, user_id=user_id_reward )
    text, _ = await format_text_profile(anket=profile[0], session=session, reward = self_reward, return_reward=True)
    text += '\nВы уверены, что хотите забрать награду именно у этого пользователя? Анкета выглядит корректно?'
    kb = await cancel_reward_inline_kb(type_reward='return')
    await state.update_data( self_reward=self_reward )
    await edit_message( message=message, text=text, markup=kb, photo=first_photo[0]['photo_id'] )
    await RewardUser.return_reward_confirm_state.set()


#Принимаем подтверждение подтверждение dp.register_callback_query_handler(reward_complete, state=RewardUser.return_reward_confirm_state)
# async def return_reward_complete(call:types.CallbackQuery, callback_data:dict=None,state:FSMContext=None):
#     callback = callback_data['callback']
#     if callback == 'confirm':
#         data = await state.get_data()
#         id_user_reward = data['id_user_reward']
#         reward = data['self_reward']
#         session = call.bot.data['session_maker']
#         await delete_reward(session=session, user_id=id_user_reward, reward=reward)
#         await call.answer('Награда удалена')
#         await verify_user(message=call)
#         await state.finish()
#     elif callback == 'wrong':
#         await call.answer('Награда оставлена')
#         await state.finish()
#         await verify_user(message=call)


#Раздел "разные ссылки"
# async def different_link_mod(message: Union[ types.Message, types.CallbackQuery]):
#     if isinstance(message, types.CallbackQuery):
#         message = message.message
#     text = 'В данном разделе вы можете изменить ссылки и описания или добавить новые'
#     session = message.bot.data['session_maker']
#     all_info = await select_different_links(session=session)
#     kb = await different_link_mod_kb(all_info)
#     await edit_message(message=message, text=text, markup=kb)

async def different_link_new(call:types.CallbackQuery, state:FSMContext=None):
    text = 'Введите описание'
    kb = await cancel_inline_kb()
    await edit_message(message=call, text=text, markup=kb)
    await NewLink.description_state.set()


async def different_link_new_description(message: types.Message, state:FSMContext=None):
    if message.text in ['Верификация','Жалобы','Наградить','Забрать награду','Разные ссылки','Рекомендации',
                        'Назначить модератора','Убрать модератора','Скачать БД']:
        await message.delete()
        await message.answer('Введите корректное описание или нажмите отмена')
        return
    description = message.text
    text = 'Введите ссылку'
    kb = await cancel_inline_kb()
    await state.update_data( description=description )
    await NewLink.link_state.set()
    await edit_message(message=message, text=text, markup=kb)

# async def different_link_new_link(message:types.Message, state:FSMContext):
#     if message.text in ['Верификация','Жалобы','Наградить','Забрать награду','Разные ссылки','Рекомендации',
#                         'Назначить модератора','Убрать модератора','Скачать БД']:
#         await message.delete()
#         await message.answer('Введите корректное описание или нажмите отмена')
#         return
#     data = await state.get_data()
#     session = message.bot.data['session_maker']
#     link = message.text
#     description = data['description']
#     await insert_different_links(session=session, link=link, description=description)
#     text = 'Добавлена запись:\n\n' \
#            f'{description}\n\n' \
#            f'{link}'
#     await edit_message(message = message, text=text)
#     await state.finish()

# async def different_link_mod_kb_func(call:types.CallbackQuery, callback_data:dict):
#     callback = callback_data['callback']
#     if callback == 'new':
#         await different_link_new(call=call)
#     elif callback == 'existing':
#         id_link = callback_data['id_link']
#         session = call.bot.data['session_maker']
#         all_info = await select_different_links_first(session=session, id_link=id_link)
#         text = f'{all_info[0]["description"]}\n\n' \
#                f'{all_info[0]["link"]}\n'
#         kb = await different_link_edit_descr_or_link(id_link=id_link)
#         await call.message.delete()
#         await call.message.answer(text=text, reply_markup=kb)
#     elif callback == 'cancel':
#         await call.message.delete()
#     await call.answer()

#обработчик при изменении описания или ссылки
# async def different_link_edit_descr_or_link_func(call:types.CallbackQuery, callback_data:dict, state:FSMContext=None):
#     callback = callback_data['callback']
#     id_link = callback_data['id_link']
#     if callback == 'description':
#         session = call.message.bot.data['session_maker']
#         all_info = await select_different_links_first(session=session, id_link=id_link)
#         text = f'Пришлите новое описание. Нажмите на описание если хотите его скопировать\n\n' \
#                f'<code>{all_info[0]["description"]}</code>\n'
#         kb = await cancel_inline_kb()
#         await call.message.delete()
#         await call.message.answer(text=text, reply_markup=kb)
#         await EditLink.description_state.set()
#         await state.update_data(id_link=id_link)
#     elif callback == 'link':
#         session = call.message.bot.data['session_maker']
#         all_info = await select_different_links_first( session=session, id_link=id_link )
#         text = f'Пришлите новую ссылку. Нажмите на ссылку если хотите её скопировать\n\n' \
#                f'<code>{all_info[0]["link"]}</code>\n'
#         kb = await cancel_inline_kb()
#         await call.message.delete()
#         await call.message.answer( text=text, reply_markup=kb )
#         await EditLink.link_state.set()
#         await state.update_data( id_link=id_link )
#     elif callback == 'delete':
#         session = call.message.bot.data['session_maker']
#         await delete_different_link(session=session, id_link=id_link)
#         text = 'Запись удалена'
#         await edit_message(message=call, text=text)
#     elif callback == 'cancel':
#         await different_link_mod(message=call)
#     await call.answer()
# async def edit_description(message:types.Message, state:FSMContext):
#     if message.text in ['Верификация','Жалобы','Наградить','Забрать награду','Разные ссылки','Рекомендации',
#                         'Назначить модератора','Убрать модератора','Скачать БД']:
#         await message.delete()
#         await message.answer('Введите корректное описание или нажмите отмена')
#         return
#     new_description = message.text
#     data = await state.get_data()
#     id_link = data['id_link']
#     session = message.bot.data['session_maker']
#     await update_different_link_or_description(session=session, id_link=id_link, description=new_description)
#     await state.finish()
#     await message.delete()
#     text = 'Опиcание изменено на: \n\n' \
#            f'{new_description}'
#     await message.answer(text=text)


# async def edit_link(message:types.Message, state:FSMContext):
#     if message.text in ['Верификация','Жалобы','Наградить','Забрать награду','Разные ссылки','Рекомендации',
#                         'Назначить модератора','Убрать модератора','Скачать БД']:
#         await message.delete()
#         await message.answer('Введите корректное описание или нажмите отмена')
#         return
#     new_link = message.text
#     data = await state.get_data()
#     id_link = data['id_link']
#     session = message.bot.data['session_maker']
#     await update_different_link_or_description(session=session, id_link=id_link, link=new_link)
#     await state.finish()
#     await message.delete()
#     text = 'Ссылка изменена на: \n\n' \
#            f'{new_link}'
#     await message.answer(text=text)


#Поиск по ИД
async def search_user_id_telegram(message:types.Message):
    text = 'В данном разделе можно осуществить поиск по ИД пользователя'
    kb = await search_user_kb()
    await edit_message(message=message, text=text, markup=kb)

async def search_user_id_telegram_func(call:types.CallbackQuery):
    text = 'Введите ИД пользователя'
    kb = await cancel_inline_kb()
    await edit_message(message=call, text=text, markup=kb)
    await SearchUser.search_user_state.set()
    await call.answer()


async def scrolling_photo_search_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page, type_profiles='search_user')
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page, type_profiles='search_user')
    elif callback == 'back':
        await search_user_id_telegram_state(message=call, user_id=user_id_anket)
    await call.answer()


async def search_user_id_telegram_state(message:Union[types.Message, types.CallbackQuery], state:FSMContext=None, user_id=None):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    if user_id is None:
        id_user = message.text
    else:
        id_user = user_id
    session = message.bot.data['session_maker']
    user_info_all = await select_user(session=session, user_id=id_user)
    logging.info(['------user_info_all-------', len(user_info_all), user_info_all])
    if len(user_info_all) < 1:
        text = 'Такого ИД нет, проверьте правильность набора ИД и повторите попытку'
        kb = await cancel_inline_kb()
        await edit_message(message=message, text=text, markup=kb)
    else:
        text = await text_verify_user(user=user_info_all[0], type_profile='search_user', session=session)
        kb = await verify_user_kb(type_profile='search_user', user_id=id_user, all_info_user=user_info_all[0])
        photos = await select_first_photo( session=session, user_id=id_user )
        if len( photos ) < 1:
            await message.delete()
            await message.answer( text=text, reply_markup=kb )
        else:
            await message.delete()
            await message.answer_photo( photo=photos[0]['photo_id'], caption=text, reply_markup=kb )
        if state:
            await state.finish()

async def confirm_guarantor_user(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id = callback_data['user_id']
    if callback == 'confirm':
        session = call.bot.data['session_maker']
        await update_user_info(session=session, user_id=user_id, guarantor='Да')
        await call.answer(text='Гарант подтвержден')
        await search_user_id_telegram_state(message=call, user_id=user_id)
    elif callback == 'wrong':
        await call.answer(text='Подтверждение гаранта отменено')
        await search_user_id_telegram_state(message=call, user_id=user_id)
    else:
        await call.message.answer('Что то пошло не так')




#Реализация рассылки
async def mailing_users(message:types.Message):
    text = 'Здесь вы можете сделать рассылку по активным пользователям'
    kb = await mailing_kb()
    await edit_message(message=message, text=text, markup=kb)


async def mailing_kb_func(call:types.CallbackQuery):
    text = 'Введите текст рассылки'
    kb = await cancel_inline_kb()
    await edit_message(message=call, text=text, markup=kb)
    await MailingState.mailing_state.set()

async def mailing_users_state(message:types.Message, state:FSMContext):
    mess = message.text
    session = message.bot.data['session_maker']
    all_users = await select_all_users_mailing(session=session)
    for user in all_users:
        try:
            await message.bot.send_message(chat_id=user['user_id'], text=mess)
        except:
            pass
        await asyncio.sleep( 0.4 )
    await message.answer(text='Рассылка отправлена')
    await state.finish()

def moderator_handler(dp: Dispatcher):
    dp.register_message_handler(verify_user, commands='start' ,is_moderator = True )
    dp.register_message_handler(verification, text='Верификация' , is_moderator = True)

    dp.register_callback_query_handler(verify_kb, verify_user_cd.filter())
    #Photo
    dp.register_callback_query_handler(scrolling_photo_moderation_cb, scrolling_photos_moderation_cd.filter())
    # no_verify_state
    dp.register_message_handler(no_verification,state=UserModeraion.no_verification_state,is_moderator = True )
    dp.register_callback_query_handler(cancel_func, cancel_cd.filter(),state=UserModeraion.no_verification_state)
    #Обработка стайта с написанием ссобщения
    dp.register_message_handler(write_moderation, state=UserModeraion.write_state)
    #жалобы
    dp.register_message_handler(complaints_moderation, text='Жалобы' ,is_moderator = True )
    dp.register_callback_query_handler(complaints_kb_func, complaints_cd.filter())
    dp.register_callback_query_handler(complaints_profile_func_cd, complaints_profile_cd.filter())
    dp.register_callback_query_handler(complaints_photo, scrolling_photos_complains_cd.filter())
    #награды
    dp.register_message_handler(reward_id, text='Наградить' ,is_moderator = True )
    dp.register_message_handler( reward_self, state=RewardUser.reward_id_state )
    dp.register_callback_query_handler(cancel_func, cancel_cd.filter(), state='*')
    dp.register_message_handler( reward_confirm, state=RewardUser.reward_state )
    # dp.register_callback_query_handler( reward_complete,cancel_reward_cd.filter(), state=RewardUser.reward_confirm_state )
    #забрать награду
    # dp.register_message_handler( return_reward_id, text='Забрать награду', is_moderator=True )
    dp.register_message_handler( return_reward_self, state=RewardUser.return_reward_id_state )
    dp.register_callback_query_handler( cancel_func, cancel_cd.filter(), state=RewardUser.return_reward_id_state )
    dp.register_message_handler( return_reward_confirm, state=RewardUser.return_reward_state )
    # dp.register_callback_query_handler( return_reward_complete, cancel_return_reward_cd.filter(), state=RewardUser.return_reward_confirm_state )
    #Разные ссылки
    # dp.register_message_handler(different_link_mod, text='Разные ссылки', is_moderator=True)
    # dp.register_callback_query_handler(different_link_mod_kb_func, different_link_CD.filter())
    #Разные ссылки новое
    dp.register_message_handler( different_link_new_description, state=NewLink.description_state)
    # dp.register_message_handler( different_link_new_link, state=NewLink.link_state)
    #Разные ссылки редактирование
    # dp.register_callback_query_handler(different_link_edit_descr_or_link_func, different_link_edit_descr_or_link_CD.filter())
    # dp.register_message_handler(edit_description, state=EditLink.description_state)
    # dp.register_message_handler(edit_link, state=EditLink.link_state)
    #Поиск по ИД
    dp.register_message_handler(search_user_id_telegram, text='Поиск по ID телеграм', is_moderator=True)
    dp.register_callback_query_handler(search_user_id_telegram_func, text='search_for_id', is_moderator=True)
    dp.register_message_handler(search_user_id_telegram_state, state=SearchUser.search_user_state)
    dp.register_callback_query_handler(scrolling_photo_search_cb, scrolling_photos_search_cd.filter())
    dp.register_callback_query_handler(confirm_guarantor_user, appoint_guarantor_confirm_cd.filter())
    dp.register_message_handler(block_user_state, state=BlockUser.block_user_state)
    #Рассылка
    dp.register_message_handler(mailing_users, text='Рассылка', is_moderator=True)
    dp.register_callback_query_handler(mailing_kb_func, text='make_newsletter', is_moderator=True)
    dp.register_message_handler(mailing_users_state, state=MailingState.mailing_state)
    #Изменение имени и фамилии
    dp.register_callback_query_handler(edit_user_moderation_cb_func, edit_user_moderation_cb.filter())
    dp.register_message_handler(edit_user_moderation_state, state=EditUserModeration)

