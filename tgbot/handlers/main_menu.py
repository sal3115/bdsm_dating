import logging
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ChatType
from aiogram.utils import exceptions

from tgbot.keyboards.inline import dating_keyboard, dating_keyboard_cb,  scrolling_photos, \
    scrolling_photos_cb, cancel_inline_kb, cancel_cd
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.states import ComplaintsUser
from tgbot.models.sql_request import select_user_anketa, select_photo, insert_like_dis, select_user, \
    select_user_profile_like, select_user_profile_like_me, select_user_profile_mutual_interest, select_first_photo, \
    insert_complaints, select_user_profile_not_interest, select_check_mutual_interest, select_check_interest, \
    insert_daily_reaktion, select_user_with_mini_id
from tgbot.services.auxiliary_functions import edit_message, profile_viewer, format_text_profile, \
    insert_like_dislake_all
from tgbot.services.photo_and_text import text_dict, text_main_menu


async def first_page(message:Union[ types.Message, types.CallbackQuery]):
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return  # Игнорируем сообщение
    if isinstance(message, types.CallbackQuery):
        message = message.message
    text = text_dict['qw_23']
    kb = await main_menu_kb()
    if message.get_args():
        arg_start = message.get_args().split('=')
        if arg_start[0] == 'profile':
            session = message.bot.data['session_maker']
            user_id_mini = arg_start[1]
            profile = await select_user_with_mini_id(session=session, user_id=user_id_mini)
            if profile[0]['user_id'] == message.chat.id:
                text = 'Это ваша анкета, если хотите посмотреть свою анкету перейдите в пункт "Изменить анкету"'
                await edit_message( message=message, text=text )
                return
            if len(profile) <=0:
                text += '\n' \
                        'Данного пользователя нет, возможно он удалился'
                await edit_message( message=message, text=text, markup=kb )
                return
            text, id_anket = await format_text_profile(anket=profile[0], session=session)
            kb = await dating_keyboard( user_id=id_anket )
            first_photo = await select_first_photo( session=session, user_id=id_anket )
            if len( first_photo ) > 0:
                photo = first_photo[0]['photo_id']
            else:
                photo = InputFile( 'tgbot/misc/no_photo.jpg' )
            await profile_viewer( message=message, text=text, photo=photo, markup=kb )
        else:
            await message.delete()
        logging.info(message)
    else:
        await edit_message( message=message, text=text, markup=kb )


async def blocking_messages(message:types.Message):
    await message.delete()


async def view_questionnaires(message:Union[types.Message, types.CallbackQuery], page=0, type_profile=None):
    if isinstance(message, types.CallbackQuery):
        callback_id = message.id
        message = message.message
    user_id = message.chat.id
    session_maker = message.bot.data['session_maker']
    logging.info(['---------type_profile---------', type_profile])
    if type_profile == 'favorites_profile':
        ankets_data= await select_user_profile_like(session=session_maker,user_id=user_id)
    elif type_profile == 'interested_me':
        ankets_data = await select_user_profile_like_me(session=session_maker, user_id=user_id)
    elif type_profile == 'mutual_interest':
        ankets_data = await select_user_profile_mutual_interest(session=session_maker, user_id=user_id)
    elif type_profile == 'not_interested_me':
        ankets_data = await select_user_profile_not_interest(session=session_maker, user_id=user_id)
    else:
        ankets_data= await select_user_anketa(session=session_maker,user_id=user_id)
    logging.info(['---------len anket---------', len(ankets_data)])
    if len(ankets_data) == 0:
        text = 'На данный момент анкет больше нет'
        await edit_message( message=message, text=text )
        return
    if page+1 > len(ankets_data):
        page = 0
    if page < 0:
        page = len(ankets_data)-1
    anket = ankets_data[0 + page]
    if type_profile == 'favorites_profile':
        text, user_id_anket = await format_text_profile( anket=anket, type_profile='favorites_profile', session=session_maker )
        kb = await dating_keyboard( user_id=user_id_anket, page=page, type_profiles='favorites_profile' )
    elif type_profile == 'interested_me':
        text, user_id_anket = await format_text_profile(anket=anket, type_profile='interested_me', session=session_maker)
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='interested_me')
    elif type_profile == 'not_interested_me':
        text, user_id_anket = await format_text_profile( anket=anket, type_profile='not_interested_me',
                                                         session=session_maker )
        kb = await dating_keyboard( user_id=user_id_anket, page=page, type_profiles='not_interested_me' )
    elif type_profile == 'mutual_interest':
        text, user_id_anket = await format_text_profile(anket=anket, type_profile='mutual_interest', session=session_maker)
        try:
            check_user_id = await message.bot.get_chat_member_count(user_id_anket)
            user_link = f'tg://user?id={user_id_anket}'
        except exceptions.ChatNotFound:
            user_name = anket['username']
            if user_name is None:
                user_link = None
            else:
                user_link = f'https://t.me/{user_name}'
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='mutual_interest', url=user_link)
    else:
        text, user_id_anket = await format_text_profile( anket=anket, session=session_maker )
        kb = await dating_keyboard(user_id=user_id_anket, page=page)
    photos = await select_first_photo( session=session_maker, user_id=user_id_anket )
    if len(photos)>0:
        photo= photos[0]['photo_id']
        await profile_viewer(message=message, text=text, photo=photo, markup=kb)
    else:
        await profile_viewer(message=message, text=text, markup=kb)


async def scrolling_photo_func(call: types.CallbackQuery, user_id_anket,page:int ,counter=0, type_profiles=None):
    session_maker = call.bot.data['session_maker']
    more_photos = await select_photo( session=session_maker, user_id=user_id_anket )
    quantity_photos = len(more_photos)
    if quantity_photos < 1:
        await call.answer(text= 'Пользователь не добавил фото')
        return
    if counter+1 > quantity_photos:
        counter = 0
    if counter <= -1:
        counter = quantity_photos-1
    current_photo = more_photos[0+counter]['photo_id']
    if type_profiles is not None:
        kb = await scrolling_photos(user_id=user_id_anket, counter=counter, page = page, type_profile=type_profiles)
    else:
        kb = await scrolling_photos(user_id=user_id_anket, counter=counter, page = page)
    await edit_message( message=call, text=f'Фото {counter + 1} из {quantity_photos}', markup=kb, photo=current_photo )


async def scrolling_photo_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page)
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page)
    elif callback == 'back':
        await view_questionnaires(message=call, page=page)


async def processing_dating_keyboard(call:types.CallbackQuery, callback_data:dict, state:FSMContext=None):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    page = int(callback_data['page'])
    user_id = call.from_user.id
    session_maker = call.bot.data['session_maker']
    user_anket = await select_user(session=session_maker, user_id=user_id_anket)
    kb = await dating_keyboard( user_id=user_id_anket, page=page )
    if callback == 'about_me':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, call_back=callback)
        text = user_anket[0]['about_my_self']
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'video_card':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, call_back=callback)
        video = user_anket[0]['video']
        if video is None:
            await call.answer('У пользователя нет видеовизитки')
        else:
            await edit_message(message=call, video=video, markup=kb)
    elif callback == 'more_photos':
        await scrolling_photo_func(call=call, user_id_anket=user_id_anket, page=page)
    elif callback == 'interesting':
        check_moderation = await select_user(session=session_maker, user_id=user_id)
        if check_moderation[0]['moderation'] == False:
            await call.answer('Вы не прошли модерацию, пожалуйста, ждите.')
            return
        else:
            check_mutual_like = await select_check_mutual_interest(session=session_maker, user_id=user_id, partner_id=user_id_anket)
            if len(check_mutual_like) > 0:
                user_name = user_anket[0]['username']
                user_link = f'https://t.me/{user_name}'
                kb = await dating_keyboard( user_id=user_id_anket, page=page, call_back=callback, url=user_link )
                await call.message.edit_reply_markup(reply_markup=kb)
                await insert_like_dislake_all(session=session_maker, user_id=user_id, partner_user_id=user_id_anket, reaction=True)
                await call.answer('У вас взаимный интерес')
                await view_questionnaires( message=call, page=page )
                try:
                    text = 'У вас взаимный интерес. ' \
                           'Зайдите в раздел «Лайки», «Взаимный интерес», чтобы начать общение.'
                    await call.bot.send_message( chat_id=user_id_anket, text=text )
                except:
                    pass
            else:
                await insert_like_dis(session=session_maker, user_id=user_id, partner_id=user_id_anket, reaction=True)
                await insert_daily_reaktion(session=session_maker, user_id=user_id, partner_id=user_id_anket, reaction=True)
                await view_questionnaires( message=call, page=page )
                try:
                    text = 'Кому-то понравилась ваша анкета. Зайдите в раздел ' \
                           '«Лайки», «Интересуются мной», чтобы узнать, кто это. '
                    await call.bot.send_message( chat_id=user_id_anket, text=text )
                except:
                    pass
    elif callback == 'dont_show':
        check_moderation = await select_user( session=session_maker, user_id=user_id )
        if check_moderation[0]['moderation'] == False:
            await call.answer( 'Вы не прошли модерацию, пожалуйста, ждите.' )
            return
        else:
            await insert_like_dislake_all(session=session_maker, user_id=user_id, partner_user_id=user_id_anket, reaction=False)
            await view_questionnaires( message=call, page=page  )
    elif callback == 'complain':
        text = 'Напишите свою жалобу'
        kb = await cancel_inline_kb()
        await edit_message(message=call, text=text, markup=kb)
        await ComplaintsUser.complaints_state.set()
        await state.update_data(user_id=user_id, complaint_user_id = user_id_anket, page=page, type_profile=None)
    elif callback == 'following_anket':
        await view_questionnaires( message=call, page=page +1)
    elif callback == 'back_anket':
        await view_questionnaires( message=call, page=page - 1 )
    elif callback == 'profile':
        await view_questionnaires(message=call, page=page)
    await call.answer()

async def cancel_kb_state_complaints(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    page = data['page']
    type_profile = data['type_profile']
    if type_profile == 'mutual_interest':
        await view_questionnaires(message=call, page=page, type_profile='mutual_interest')
    elif type_profile is None:
        await view_questionnaires(message=call, page=page)




async def complaint_state_func(message: types.Message, state:FSMContext):
    session = message.bot['session_maker']
    data = await state.get_data()
    user_id = data['user_id']
    complaint_user_id = data['complaint_user_id']
    page = data['page']
    complaint_text = message.text
    await insert_complaints(session=session, id_user=user_id, id_user_complaints=complaint_user_id, complaints=complaint_text)
    await state.finish()
    text = 'Жалоба передана модераторам'
    await edit_message(message=message, text=text)

#кнопка полезные советы
async def useful_tips(message:types.Message):
    text = text_main_menu['useful_tips']
    await message.answer(text=text)


async def support_func(message:types.Message):
    text = text_main_menu['support']
    await edit_message(message=message, text=text)

async def no_moderation_user_answer(message:types.Message):
    text = 'Вы не прошли модерацию, пожалуйста, подождите'
    await edit_message(message=message, text=text)

async def block_user(message: types.Message):
    text = 'Вы заблокированы. Для уточнения обратитесь в поддержку'
    kb = await main_menu_kb(status_user='block_user')
    await edit_message(message=message, text=text, markup = kb )

def main_menu_handler(dp:Dispatcher):
    dp.register_message_handler(view_questionnaires, text='Анкеты',is_user = True, check_user_in_moderation=True)
    dp.register_message_handler(no_moderation_user_answer, text='Анкеты',is_user = True)


    dp.register_message_handler(first_page, commands='start' ,is_user = True )

    dp.register_callback_query_handler(scrolling_photo_cb, scrolling_photos_cb.filter())
    #Состояние жалобы на пользователя
    dp.register_message_handler(complaint_state_func, state=ComplaintsUser.complaints_state)
    dp.register_callback_query_handler(cancel_kb_state_complaints, cancel_cd.filter(), state=ComplaintsUser.complaints_state)

    dp.register_callback_query_handler(processing_dating_keyboard, dating_keyboard_cb.filter())
    # dp.register_message_handler(blocking_messages, content_types=types.ContentType.ANY)
    #Ловим нажатие на кнопку Полезные советы
    dp.register_message_handler(support_func, text='Поддержка',is_user = True)

    dp.register_message_handler( support_func, text='Поддержка', is_user_exit=True )
    #Заблокированый пользователь
    dp.register_message_handler( support_func, text='Поддержка', is_user_block=True )
    dp.register_message_handler( block_user, is_user_block=True )
