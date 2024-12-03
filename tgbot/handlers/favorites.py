import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.handlers.main_menu import scrolling_photo_func, view_questionnaires, first_page, no_moderation_user_answer
from tgbot.keyboards.inline import favorite_profile_kb, interesting_cb, \
    dating_keyboard_favorites_cb, scrolling_photos_fav_cb, dating_keyboard, \
    scrolling_photos_inter_me_cb, dating_keyboard_interested_me_cb, dating_keyboard_mutual_interest_cb, \
    scrolling_photos_mutual_interest_cb, cancel_inline_kb, dating_keyboard_not_interested_me_cb, \
    scrolling_photos_not_inter_me_cb
from tgbot.misc.states import ComplaintsUser
from tgbot.models.sql_request import select_user_profile_like, select_photo, select_user, insert_like_dis, \
    delete_reaction, insert_daily_reaktion
from tgbot.services.auxiliary_functions import edit_message, check_like_dislike, insert_like_dislake_all


async def favourites_profile_no_paid(message: types.Message):
    text = 'Для просмотра данного раздела оформите подписку\nИзменить анкету ➡️ Оформить подписку'
    await edit_message(message=message, text=text)

async def favourites_profile(message:types.Message, last_message_id=None):
    text = '''На данной странице вы можете посмотреть:
Пользователей которые понравились вам - "Понравились мне"
Пользователей которым понравились вы - "Интересуются мной"
Пользователей которые понравились вам и понравились вы - "Взаимный интерес"    
    '''
    logging.info(last_message_id)
    user_id = message.chat.id
    kb = await favorite_profile_kb(user_id=user_id, page=0)
    await edit_message(message=message, text=text, markup=kb)


async def scrolling_photo_favorites_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page, type_profiles='favorites_profile')
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page, type_profiles='favorites_profile')
    elif callback == 'back':
        await view_questionnaires(message=call, page=page, type_profile='favorites_profile')



async def favorites_profile_cb(call: types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    page = int( callback_data['page'] )
    user_id = call.from_user.id

    if callback == 'liked_them':
        await view_questionnaires(message=call, type_profile='favorites_profile')
    elif callback == 'interested_me':
        await view_questionnaires(message=call, type_profile='interested_me')
    elif callback == 'mutual_interest':
        await view_questionnaires(message=call, type_profile='mutual_interest')
    elif callback == 'not_interested_me':
        await view_questionnaires(message=call, type_profile='not_interested_me')
    elif callback == 'back':
        await first_page(message=call)

async def favorites_profile_cb_not_paid(call: types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    if callback == 'mutual_interest':
        await view_questionnaires(message=call, type_profile='mutual_interest')
    else:
        text = 'Для просмотра данного раздела оформите подписку\nИзменить анкету ➡️ Оформить подписку'
        kb = await favorite_profile_kb( user_id=user_id_anket, page=0 )
        await edit_message(message=call, text=text, markup=kb)

async def processing_favourites_keyboard(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    page = int(callback_data['page'])
    user_id = call.from_user.id
    session_maker = call.bot.data['session_maker']
    user_anket = await select_user(session=session_maker, user_id=user_id_anket)
    kb = await dating_keyboard( user_id=user_id_anket, page=page, type_profiles='favorites_profile')
    if callback == 'about_me':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='favorites_profile', call_back='about_me')
        text = user_anket[0]['about_my_self']
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'video_card':
        video = user_anket[0]['video']
        logging.info(f'---------video--------------')
        logging.info(f'---------{video}--------------')
        if video is None:
            await call.answer('У пользователя нет видеовизитки')
        else:
            kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='favorites_profile',
                                       call_back='video_card')
            await edit_message(message=call, video=video, markup=kb)
    elif callback == 'more_photos':
        await scrolling_photo_func(call=call, user_id_anket=user_id_anket, page=page, type_profiles='favorites_profile')
    elif callback == 'interesting':
        await view_questionnaires(message=call, page=page+1, type_profile='favorites_profile')
        await insert_like_dislake_all( session=session_maker, user_id=user_id, partner_user_id=user_id_anket, reaction=True)
    elif callback == 'remove_like':
        await delete_reaction(session=session_maker, user_id=user_id, id_partner=user_id_anket)
        await view_questionnaires( message=call, page=page + 1, type_profile='favorites_profile' )
    elif callback == 'complain':
        text = 'Напишите свою жалобу'
        kb = await cancel_inline_kb()
        await edit_message( message=call, text=text, markup=kb )
        await ComplaintsUser.complaints_state.set()
    elif callback == 'following_anket':
        await view_questionnaires( message=call, page=page +1, type_profile='favorites_profile')
    elif callback == 'profile':
        await view_questionnaires(message=call, page=page, type_profile='favorites_profile')
    await call.answer()

#------------------intresting_me------------------------


async def scrolling_photo_interested_me_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page, type_profiles='interested_me')
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page, type_profiles='interested_me')
    elif callback == 'back':
        await view_questionnaires(message=call, page=page, type_profile='interested_me')


async def processing_interested_me_keyboard(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    page = int(callback_data['page'])
    user_id = call.from_user.id
    session_maker = call.bot.data['session_maker']
    user_anket = await select_user(session=session_maker, user_id=user_id_anket)
    kb = await dating_keyboard( user_id=user_id_anket, page=page, type_profiles='interested_me')
    if callback == 'about_me':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='interested_me', call_back=callback)
        text = user_anket[0]['about_my_self']
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'video_card':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='interested_me', call_back=callback)
        video = user_anket[0]['video']
        logging.info(f'---------video--------------')
        logging.info(f'---------{video}--------------')
        if video is None:
            await call.answer('У пользователя нет видеовизитки')
        else:
            await edit_message(message=call, video=video, markup=kb)
    elif callback == 'more_photos':
        await scrolling_photo_func(call=call, user_id_anket=user_id_anket, page=page, type_profiles='interested_me')
    elif callback == 'interesting':
        await view_questionnaires(message=call, page=page+1, type_profile='interested_me')
        await insert_like_dislake_all( session=session_maker, user_id=user_id, partner_user_id=user_id_anket,
                                       reaction=True )
    elif callback == 'dont_show':
        await insert_like_dislake_all( session=session_maker, user_id=user_id, partner_user_id=user_id_anket,
                                       reaction=False )
        await view_questionnaires( message=call, page=page + 1, type_profile='interested_me' )
    elif callback == 'complain':
        text = 'Напишите свою жалобу'
        kb = await cancel_inline_kb()
        await edit_message( message=call, text=text, markup=kb )
        await ComplaintsUser.complaints_state.set()
    elif callback == 'following_anket':
        await view_questionnaires( message=call, page=page +1, type_profile='interested_me')
    elif callback == 'profile':
        await view_questionnaires(message=call, page=page, type_profile='interested_me')

    await call.answer()

#------------------not interested --------------------
async def processing_not_interested_me_keyboard(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    page = int(callback_data['page'])
    user_id = call.from_user.id
    session_maker = call.bot.data['session_maker']
    user_anket = await select_user(session=session_maker, user_id=user_id_anket)
    kb = await dating_keyboard( user_id=user_id_anket, page=page, type_profiles='not_interested_me')
    if callback == 'about_me':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='not_interested_me', call_back=callback)
        text = user_anket[0]['about_my_self']
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'video_card':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='not_interested_me', call_back=callback)
        video = user_anket[0]['video']
        logging.info(f'---------video--------------')
        logging.info(f'---------{video}--------------')
        if video is None:
            await call.answer('У пользователя нет видеовизитки')
        else:
            await edit_message(message=call, video=video, markup=kb)
    elif callback == 'more_photos':
        await scrolling_photo_func(call=call, user_id_anket=user_id_anket, page=page, type_profiles='not_interested_me')
    elif callback == 'interesting':
        await view_questionnaires(message=call, page=page+1, type_profile='not_interested_me')
        await insert_like_dislake_all( session=session_maker, user_id=user_id, partner_user_id=user_id_anket,
                                       reaction=True )
    elif callback == 'remove_dislike':
        await delete_reaction(session=session_maker, user_id=user_id, id_partner=user_id_anket)
        await view_questionnaires( message=call, page=page + 1, type_profile='not_interested_me' )
    elif callback == 'complain':
        text = 'Напишите свою жалобу'
        kb = await cancel_inline_kb()
        await edit_message( message=call, text=text, markup=kb )
        await ComplaintsUser.complaints_state.set()
    elif callback == 'following_anket':
        await view_questionnaires( message=call, page=page +1, type_profile='not_interested_me')
    elif callback == 'profile':
        await view_questionnaires(message=call, page=page, type_profile='not_interested_me')

    await call.answer()


async def scrolling_photo_not_interested_me_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page, type_profiles='not_interested_me')
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page, type_profiles='not_interested_me')
    elif callback == 'back':
        await view_questionnaires(message=call, page=page, type_profile='not_interested_me')


#------------------mutual_interest------------------------


async def scrolling_photo_mutual_interest_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int(callback_data['counter'])
    page = int(callback_data['page'])
    if callback == 'previous_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter-1, page=page, type_profiles='mutual_interest')
    elif callback == 'next_photo':
        await scrolling_photo_func(call = call, user_id_anket=user_id_anket, counter=counter+1, page=page, type_profiles='mutual_interest')
    elif callback == 'back':
        await view_questionnaires(message=call, page=page, type_profile='mutual_interest')

async def processing_mutual_interest_keyboard(call:types.CallbackQuery, callback_data:dict, state:FSMContext=None):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    page = int(callback_data['page'])
    user_id = call.from_user.id
    session_maker = call.bot.data['session_maker']
    user_anket = await select_user(session=session_maker, user_id=user_id_anket)
    kb = await dating_keyboard( user_id=user_id_anket, page=page, type_profiles='mutual_interest')
    if callback == 'about_me':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='mutual_interest', call_back=callback)
        text = user_anket[0]['about_my_self']
        await edit_message(message=call, text=text, markup=kb)
    elif callback == 'video_card':
        kb = await dating_keyboard(user_id=user_id_anket, page=page, type_profiles='mutual_interest', call_back=callback)
        video = user_anket[0]['video']
        logging.info(f'---------video--------------')
        logging.info(f'---------{video}--------------')
        if video is None:
            await call.answer('У пользователя нет видеовизитки')
        else:
            await edit_message(message=call, video=video, markup=kb)
    elif callback == 'more_photos':
        await scrolling_photo_func(call=call, user_id_anket=user_id_anket, page=page, type_profiles='mutual_interest')
    elif callback == 'interesting':
        await view_questionnaires(message=call, page=page+1, type_profile='mutual_interest')
        await insert_like_dislake_all( session=session_maker, user_id=user_id, partner_user_id=user_id_anket,
                                       reaction=True )
    elif callback == 'dont_show':
        await view_questionnaires( message=call, page=page + 1, type_profile='mutual_interest' )
        await insert_like_dislake_all( session=session_maker, user_id=user_id, partner_user_id=user_id_anket,
                                       reaction=False )
    elif callback == 'profile':
        await view_questionnaires( message=call, page=page, type_profile='mutual_interest' )
    elif callback == 'following_anket':
        await view_questionnaires( message=call, page=page +1, type_profile='mutual_interest')
    elif callback == 'complain':
        text = 'Напишите свою жалобу'
        kb = await cancel_inline_kb()
        await edit_message( message=call, text=text, markup=kb )
        await ComplaintsUser.complaints_state.set()
        await state.update_data( user_id=user_id, complaint_user_id=user_id_anket, page=page, type_profile='mutual_interest' )
    await call.answer()


def favorites_handler(dp):
    # dp.register_message_handler(favourites_profile, text='Лайки',is_user = True, is_paid = True, check_user_in_moderation=True)
    dp.register_message_handler(favourites_profile, text='Лайки',is_user = True)
    dp.register_callback_query_handler(favorites_profile_cb, interesting_cb.filter(), is_paid = True, check_user_in_moderation=True)
    dp.register_callback_query_handler(favorites_profile_cb_not_paid, interesting_cb.filter())
    dp.register_callback_query_handler(processing_favourites_keyboard, dating_keyboard_favorites_cb.filter())
    dp.register_callback_query_handler(scrolling_photo_favorites_cb, scrolling_photos_fav_cb.filter())
    #intersting me
    dp.register_callback_query_handler(processing_interested_me_keyboard,dating_keyboard_interested_me_cb.filter(), is_paid = True, check_user_in_moderation=True)
    dp.register_callback_query_handler(scrolling_photo_interested_me_cb,scrolling_photos_inter_me_cb.filter())
    #not interested me
    dp.register_callback_query_handler(processing_not_interested_me_keyboard, dating_keyboard_not_interested_me_cb.filter(), is_paid = True, check_user_in_moderation=True)
    dp.register_callback_query_handler(scrolling_photo_not_interested_me_cb, scrolling_photos_not_inter_me_cb.filter())
    #mutual_interest
    dp.register_callback_query_handler(processing_mutual_interest_keyboard, dating_keyboard_mutual_interest_cb.filter())
    dp.register_callback_query_handler(scrolling_photo_mutual_interest_cb, scrolling_photos_mutual_interest_cb.filter())
