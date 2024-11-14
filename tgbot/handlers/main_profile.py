import datetime
import logging
from typing import Union, List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType
from aiogram.utils.exceptions import MessageNotModified
from dateutil.relativedelta import relativedelta

from tgbot.handlers.edit_profile import first_edit_profile
from tgbot.handlers.main_menu import first_page, scrolling_photo_func
from tgbot.handlers.update_photo_table import update_photo_func
from tgbot.keyboards.inline import my_profile_cd, my_profile_kb, edit_my_photos_kb, my_photos_cd, edit_video_card_kb, \
    my_video_card_cd, cancel_inline_kb, cancel_cd, view_my_profile_cd, view_my_profile_keyboard, \
    scrolling_photos_main_cd, paid_subs_kb, paid_subs_cd
from tgbot.keyboards.reply import main_menu_kb, cancel_kb
from tgbot.misc.states import EditOther
from tgbot.models.sql_request import select_user_anketa, select_user, update_user_info, select_photo, \
    update_first_photo, select_first_photo, insert_photo, delete_photo_in_table, select_video_card, \
    select_rejection_user, select_price_subscription, insert_paid_subscription, NumberOfDays
from tgbot.services.auxiliary_functions import edit_message, add_photo_func, format_text_profile



async def changing_moderation(session, user_id):
    rejections_user = await select_rejection_user(session=session, user_id=user_id)
    if len(rejections_user) > 0:
        await update_user_info(session=session, user_id=user_id,status = 'user', moderation = False )
    else:
        await update_user_info(session=session, user_id=user_id,moderation = False)


async def cancel_func(message:types.Message, state: FSMContext):
    logging.info('-------------cancel kb-------------')
    await state.finish()
    text = 'Вы отменили редактирование'
    kb = await main_menu_kb()
    await edit_message(message=message, text=text, markup=kb)


async def my_profile(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    text = 'Тут вы можете внести изменения в вашу анкету. Придется немного подождать пока она пройдет повторную модерацию'
    user_id = message.chat.id
    kb = await my_profile_kb( user_id=user_id )
    await edit_message( message=message, text=text, markup=kb )


async def about_me_edit(message:Union[types.Message, types.CallbackQuery], state: FSMContext=None):
    if isinstance(message, types.CallbackQuery):
        message = message.message
    user_id = message.chat.id
    kb = await cancel_kb()
    session_maker = message.bot.data['session_maker']
    user_anket = await select_user( session=session_maker, user_id=user_id )
    about_me = user_anket[0]['about_my_self']
    logging.info(len(about_me))
    text = f'Здесь ты можешь поменять пункт "обо мне". Если хотите поменять на основании предыдущего просто нажмите на текст находящийся в ' \
           f'звездочке и оно скопируется, далее вставьте и отредактируйте\n'
    text1 =f'*<code>{about_me}</code>*'
    if len(text) + len(text1) > 4096:
        await edit_message( message=message, text=text)
        await message.answer(text=text1, reply_markup=kb)
    else:
        text+=text1
        await edit_message(message=message, text=text, markup=kb)
    await EditOther.about_me_state.set()

async def about_me_edit_complete(message: types.Message, state: FSMContext):
    about_my_self = message.text
    session_maker = message.bot.data['session_maker']
    user_id = message.chat.id
    logging.info([f'userid: {user_id}', f'Длина о себе: {len(about_my_self)}'])
    await update_user_info(session=session_maker, user_id=user_id, about_my_self=about_my_self)
    await state.finish()
    await changing_moderation(session=session_maker, user_id=user_id)
    text = 'Вы изменили пункт "О себе"'
    kb = await main_menu_kb()
    await edit_message(message=message, text=text, markup=kb)


#Edit photo
async def edit_my_photo(call: Union[types.CallbackQuery, types.Message], user_id,counter=0):
    session_maker = call.bot.data['session_maker']
    more_photos = await select_photo( session=session_maker, user_id=user_id )
    quantity_photos = len( more_photos )
    if quantity_photos < 1:
        kb = await edit_my_photos_kb(user_id=user_id, counter=counter,no_foto=True)
        await edit_message(message=call, text=f'У вас нет фото нажмите "Добавить"', markup=kb)
        return
    if counter + 1 > quantity_photos:
        counter = 0
    if counter <= -1:
        counter = quantity_photos - 1
    current_photo = more_photos[0 + counter]['photo_id']
    first_photo = more_photos[0 + counter]['is_first_photo']
    kb = await edit_my_photos_kb(user_id=user_id, counter=counter, first_photo=first_photo)
    await edit_message( message=call, text=f'Фото {counter + 1} из {quantity_photos}', markup=kb, photo=current_photo )


async def edit_my_first_photo(call: types.CallbackQuery, counter):
    session_maker = call.bot.data['session_maker']
    user_id = call.message.chat.id
    logging.info(['-------------user_id----------', user_id])
    photos = await select_photo(session=session_maker, user_id=user_id)
    first_photo_all = await select_first_photo( session=session_maker, user_id=user_id )
    quantity_photos = len( first_photo_all )
    if quantity_photos > 1:
        for p in first_photo_all[0]['photo_id']:
            await update_first_photo( session=session_maker, user_id=user_id, photo_id=p, first_photo=False)
    elif quantity_photos <=0:
        pass
    else:
        first_photo_id = first_photo_all[0]['photo_id']
        await update_first_photo( session=session_maker, user_id=user_id, photo_id=first_photo_id, first_photo=False )
    photo_id = photos[0+counter]['photo_id']
    logging.info(['-------------photo_id----------', photo_id ])
    await update_first_photo(session=session_maker, user_id=user_id, photo_id=photo_id, first_photo=True)
    kb = await edit_my_photos_kb( user_id=user_id, counter=counter, first_photo=True )
    try:
        await call.message.edit_reply_markup( reply_markup=kb )
        await call.answer('Главное фото изменено')
    except MessageNotModified:
        await call.answer('Данное фото является главной')
        pass


async def add_my_photo(message: Union[types.Message, types.CallbackQuery]):
    logging.info(['------------add_my_photo------------'])
    text = 'Прикрепите фото которые хотите добавить'
    kb = await cancel_inline_kb()
    await edit_message(message=message, text=text, markup=kb)
    await EditOther.my_photo_state.set()
    logging.info(['------------add_my_photo_end------------'])

async def add_my_photo_state(message: types.Message, state:FSMContext ,album: List[types.Message]= None):
    logging.info(['------------add_my_photo_state------------'])
    session_maker = message.bot.data['session_maker']
    user_id = message.chat.id
    if message.photo:
        photo = message.photo
        photos = await add_photo_func(photo=photo, album=album)
        if len(photos) == 1:
            file_id = photos[0]['file_id']
            unique_id = photos[0]['unique_id']
            await insert_photo(session=session_maker, user_id=user_id, photo_id=file_id, unique_id=unique_id )
            await state.finish()
        elif len(photos) > 1:
            for photo in photos:
                file_id = photo['file_id']
                unique_id = photo['unique_id']
                await insert_photo( session=session_maker, user_id=user_id, photo_id=file_id, unique_id=unique_id )
            await state.finish()
        else:
            await message.answer('Что то пошло не так')
            await state.finish()
        info_first_photo = await select_first_photo(session=session_maker, user_id=user_id)
        if len(info_first_photo) < 1:
            first_photo_id = photos[0]['file_id']
            await update_first_photo(session=session_maker, user_id=user_id, photo_id=first_photo_id)
        await changing_moderation( session=session_maker, user_id=user_id )
        await edit_my_photo(call=message, user_id=user_id)
        logging.info(['-----------photos-----------', photos])
        logging.info(['-----------len photos-----------', len(photos)])
    else:
        await message.delete()


async def delete_my_photo(call:types.CallbackQuery):
    session_maker = call.bot.data['session_maker']
    unique_id = call.message.photo[-1].file_unique_id
    user_id = call.message.chat.id
    info_first_photo = await select_first_photo( session=session_maker, user_id=user_id )
    await delete_photo_in_table( session=session_maker, user_id=user_id, unique_id=unique_id )
    if unique_id == info_first_photo[0]['unique_id']:
        all_photos = await select_photo( session=session_maker, user_id=user_id )
        if len(all_photos) >0:
            first_photo_id = all_photos[0]['photo_id']
            await update_first_photo( session=session_maker, user_id=user_id, photo_id=first_photo_id )
    await call.answer('Фото удалено')
    await edit_my_photo(call=call, user_id=user_id)

async def scrolling_my_photo_cb(call: types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id = call.message.chat.id
    counter = int(callback_data['counter'])
    if callback == 'previous_photo':
        await edit_my_photo(call = call, user_id=user_id, counter=counter-1)
    elif callback == 'next_photo':
        await edit_my_photo(call = call, user_id=user_id, counter=counter+1)
    elif callback == 'assign_main':
        await edit_my_first_photo(call=call, counter=counter)
    elif callback == 'add_photo':
        await add_my_photo(message=call)
    elif callback == 'delete_photo':
        await delete_my_photo(call=call)
    elif callback == 'back':
        await my_profile(message=call)
    await call.answer()



#edit video card
async def edit_my_video_card(message:Union[types.CallbackQuery, types.Message], user_id):
    if isinstance(message, types.CallbackQuery):
        message= message.message
    session_maker = message.bot.data['session_maker']
    user_id = message.chat.id
    video_card = await select_video_card(session = session_maker, user_id=user_id)
    logging.info([f'-----------------video_card------------, {video_card}', len(video_card)])
    kb = await edit_video_card_kb( user_id=user_id )
    if video_card[0]['video'] is None:
        kb = await edit_video_card_kb(user_id=user_id, no_video=True)
        text = 'У вас нет видеовизитки.\nНажмите кнопку "Добавить" и добавьте видеовизитку'
        await edit_message(message=message, text=text, markup=kb)
    else:
        text = 'Ваша видеовизитка'
        await edit_message(message=message,video= video_card[0]['video'],markup=kb, text=text)


async def edit_my_video_card_update(call: types.CallbackQuery):
    text = 'Прикрепите видеовизитку'
    kb = await cancel_inline_kb()
    await edit_message(message=call, text=text, markup=kb)
    await EditOther.my_video_card_state.set()

async def cancel_inline_update(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    text = 'Вы отменили редактирование'
    kb = await main_menu_kb()
    await edit_message( message=call, text=text, markup=kb )


async def edit_my_video_card_update_state(message: types.Message, state:FSMContext):
    session_maker = message.bot.data['session_maker']
    user_id = message.chat.id
    if message.video or message.video_note:
        video_id = message.video.file_id if message.video else message.video_note.file_id
        await update_user_info(session=session_maker, user_id=user_id, video=video_id)
        await state.finish()
        await changing_moderation( session=session_maker, user_id=user_id )
        await edit_my_video_card(message=message, user_id=user_id)
    else:
        await message.delete()


async def edit_my_video_card_delete(call: types.CallbackQuery):
    session_maker = call.message.bot.data['session_maker']
    user_id = call.message.chat.id
    await update_user_info( session=session_maker, user_id=user_id, video=None )
    await call.answer('Видеовизитка удалена')
    await edit_my_video_card( message=call, user_id=user_id )


async def edit_my_video_card_callback(call:types.CallbackQuery, callback_data: dict):
    callback = callback_data['callback']
    user_id = call.message.chat.id
    if callback == 'update_video_card':
        await edit_my_video_card_update(call=call)
    elif callback == 'delete_video_card':
        await edit_my_video_card_delete(call=call)

# просмотр собственного профиля
async def view_my_profile(call:types.CallbackQuery):
    session = call.bot.data['session_maker']
    user_id = call.message.chat.id
    data_user = await select_user(session=session, user_id=user_id)
    text, _ = await format_text_profile(anket=data_user[0], session=session)
    first_photo = await select_first_photo(session=session, user_id=user_id)
    if len(first_photo)> 0:
        first_photo = first_photo[0]['photo_id']
    else:
        first_photo=None
    kb = await view_my_profile_keyboard()
    await edit_message(message=call, text=text, photo=first_photo if first_photo else None, markup=kb)


async def view_my_profile_callback(call:types.CallbackQuery, callback_data:dict=None):
    callback = callback_data['callback']
    user_id = call.message.chat.id
    logging.info( ['______procising user_id', user_id] )
    session_maker = call.bot.data['session_maker']
    user_anket = await select_user( session=session_maker, user_id=user_id )
    text = None
    if callback == 'about_me':
        text = user_anket[0]['about_my_self']
    elif callback == 'video_card':
        logging.info( f'---------video--------------' )
    elif callback == 'more_photos':
        await scrolling_photo_func( call=call, user_id_anket=user_id, page=0, type_profiles='main_profile' )
        return
    elif callback == 'profile':
        await view_my_profile(call=call)
    kb = await view_my_profile_keyboard(call_back=callback)
    await edit_message( message=call, text=text, markup=kb)

async def scroll_photo_main_profile(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id_anket = callback_data['user_id']
    counter = int( callback_data['counter'] )
    page = int( callback_data['page'] )
    if callback == 'previous_photo':
        await scrolling_photo_func( call=call, user_id_anket=user_id_anket, counter=counter - 1, page=page,
                                    type_profiles='main_profile' )
    elif callback == 'next_photo':
        await scrolling_photo_func( call=call, user_id_anket=user_id_anket, counter=counter + 1, page=page,
                                    type_profiles='main_profile' )
    elif callback == 'back':
        await view_my_profile(call=call)
    await call.answer()


async def paid_subscription(call: types.CallbackQuery):
    session_maker = call.bot.data['session_maker']
    data = await select_price_subscription( session=session_maker )
    text = 'Подписка позволяет писать и смотреть тех кто лайкнул тебя и лайкнуть в ответ, а так же писать сообщения ' \
           'без взаимной симпатии\n'
    for dat in data:
        text += f'{dat["title"]}: {int(dat["price"])} рублей\n'
    user_id = call.message.chat.id
    kb = await paid_subs_kb(data = data,user_id=user_id)
    await call.message.answer(text=text, reply_markup=kb)


async def paid_subs_processor(call: types.CallbackQuery, callback_data:dict):
    await call.bot.delete_message(call.from_user.id, call.message.message_id)
    session = call.bot.data['session_maker']
    price_all_info = await select_price_subscription(session=session)
    price_id = callback_data['id_price']
    price = ''
    title = ''
    number_of_day = ''
    yootoken = call.bot['config'].yootoken.yootoken
    logging.info(f'----------token{yootoken}')
    for p in price_all_info:
        if int(p['id']) == int(price_id):
            title = p['title']
            price = p['price']
            number_of_day = p['number_of_days']
        else:
            pass
    logging.info(f'----------price-{price}, title - {title}')
    await call.bot.send_invoice(chat_id=call.message.chat.id, title = 'Оформление подписки', description= title,
                                payload=f'{number_of_day}', provider_token=yootoken,currency='RUB',
                                start_parameter= 'subscription', prices=[{'label': 'руб', 'amount': int(price)*100}])

async def procces_pre_paid_subs(pre_check_query: types.PreCheckoutQuery):
    user_id = pre_check_query.from_user.id
    # try:
    logging.info(pre_check_query)
    session = pre_check_query.bot['session_maker']
    number_of_day = pre_check_query.invoice_payload


    # logging.info(f'----------------------------------------------------------- {date_before}, {type(date_before)} ')
    try:
        await insert_paid_subscription(session=session, user_id=user_id, number_of_day=number_of_day)
    except NumberOfDays:
        await pre_check_query.bot.send_message(chat_id=user_id, text='Что то пошло не так обратитесь к администрации')
        return
    await pre_check_query.bot.answer_pre_checkout_query( pre_check_query.id, ok=True )
    # except:
    #     text = 'Что то пошло не так'
    #     await pre_check_query.bot.send_message(chat_id=user_id, text=text)


async def pay_paid_subs(message:types.Message):
    logging.info(f'----------------------{message.successful_payment}')
    await message.answer( 'Вы подписны на бота' )

    # try:
    #     session = message.bot['session_maker']
    #     user_id = message.chat.id
    #     number_of_day = message.successful_payment.invoice_payload
    #     await insert_paid_subscription(session=session, user_id=user_id, number_of_days=int(number_of_day))
    #     await message.answer('Вы подписны на бота')
    # except:
    #     return
    # else:
    #     await message.answer('xxxxxxxxxxxxxx')
#My profile callback
async def my_profile_callback(call:types.CallbackQuery, callback_data:dict):
    callback = callback_data['callback']
    user_id = callback_data['user_id']
    if callback == 'edit_profile':
        await first_edit_profile(message=call)
    elif callback == 'edit_about_me':
        await about_me_edit(message=call)
    elif callback == 'edit_photo':
        await edit_my_photo(call=call, user_id=user_id)
    elif callback == 'get_subscribe':
        await paid_subscription(call=call)
    elif callback == 'view_profile':
        await view_my_profile(call=call)
    await call.answer()





def main_profile_handler(dp:Dispatcher):
    dp.register_message_handler(my_profile, text='Изменить анкету',is_user = True)
    # dp.register_message_handler(my_profile_plug, text='Моя анкета')
    dp.register_callback_query_handler(my_profile_callback, my_profile_cd.filter())

    dp.register_message_handler(cancel_func, text='Отмена', state=EditOther.about_me_state)
    dp.register_message_handler(about_me_edit_complete,state=EditOther.about_me_state)
    #my photo
    dp.register_callback_query_handler(scrolling_my_photo_cb, my_photos_cd.filter())
    # dp.register_message_handler(cancel_func, text='Отмена', state=EditOther.my_photo_state)
    dp.register_callback_query_handler(cancel_inline_update, cancel_cd.filter(), state=EditOther.my_photo_state)

    dp.register_message_handler(add_my_photo_state, state=EditOther.my_photo_state, content_types=types.ContentType.ANY)
    #my video_card
    dp.register_callback_query_handler(edit_my_video_card_callback, my_video_card_cd.filter())
    dp.register_callback_query_handler(cancel_inline_update, cancel_cd.filter(), state=EditOther.my_video_card_state)

    dp.register_message_handler(cancel_func, text='Отмена', state=EditOther.my_video_card_state)
    dp.register_message_handler(edit_my_video_card_update_state, state=EditOther.my_video_card_state, content_types=types.ContentType.ANY)
    # view my profile
    dp.register_callback_query_handler(view_my_profile_callback, view_my_profile_cd.filter())
    dp.register_callback_query_handler(scroll_photo_main_profile,scrolling_photos_main_cd.filter())
    #paid
    dp.register_callback_query_handler(paid_subs_processor, paid_subs_cd.filter())
    dp.register_pre_checkout_query_handler(procces_pre_paid_subs)
    dp.register_message_handler(pay_paid_subs, content_types=ContentType.SUCCESSFUL_PAYMENT)