import logging
from typing import Union, List

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from tgbot.keyboards.inline import my_profile_new_cd, edit_profile_cd, edit_profile_kb, my_photos_cd, cancel_cd, \
    cancel_inline_kb, edit_my_photos_kb, yes_no_kb, yes_no_cb_new, interaction_format_button, interaction_format_cb
from tgbot.keyboards.reply import cancel_kb, main_menu_kb
from tgbot.misc.states import EditOther
from tgbot.models.sql_request import select_user, update_user_info, select_rejection_user, update_first_photo, \
    select_photo, delete_photo_in_table, select_first_photo, insert_photo
from tgbot.services.anketa_utulites import checking_russian_letters
from tgbot.services.auxiliary_functions import edit_message, text_separator, add_photo_func, profile_viewer, \
    date_formats, check_city


async def cancel_inline_update(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    text = 'Вы отменили редактирование'
    kb = await main_menu_kb()
    await edit_message( message=call, text=text, markup=kb )
async def changing_moderation(session, user_id):
    rejections_user = await select_rejection_user(session=session, user_id=user_id)
    if len(rejections_user) > 0:
        await update_user_info(session=session, user_id=user_id,status = 'user', moderation = False )
    else:
        await update_user_info(session=session, user_id=user_id,moderation = False)
async def my_profile_edit_process(callback: Union[types.CallbackQuery, types.Message]):
    text = 'Выберете что хотите поменять'
    kb = await edit_profile_kb()
    await edit_message(message=callback, text=text, markup=kb)


async def edit_about_me(callback:types.CallbackQuery):
    if isinstance(callback, types.CallbackQuery):
        message = callback.message
    user_id = message.chat.id
    kb = await cancel_inline_kb()
    session_maker = message.bot.data['session_maker']
    user_anket = await select_user( session=session_maker, user_id=user_id )
    about_me = user_anket[0]['about_my_self']
    logging.info(len(about_me))
    text = f'Здесь ты можешь поменять пункт "обо мне". Если хотите поменять на основании предыдущего просто нажмите на текст находящийся в ' \
           f'звездочке и оно копируется, далее вставьте и отредактируйте\n'\

    if len(about_me) > 4000:
        about_my_self_new = await text_separator( text=about_me )
        if len( about_my_self_new ) > 1:
            for mess in about_my_self_new:
                await message.answer( text=f'*<code>{mess}</code>*' )
        else:
            await message.answer( text=f'*<code>{about_me}</code>*' )
    else:
        text += f'*<code>{about_me}</code>*'
        await edit_message(message=callback, text=text, markup=kb)
    await EditOther.about_me_state.set()

async def edit_about_me_state(message:types.Message, state:FSMContext):
    about_my_self = message.text
    if len(about_my_self) > 4000:
        about_my_self_new = await text_separator(text=about_my_self)
        if len(about_my_self_new) > 1:
            for mess in about_my_self_new:
                await message.answer(text=f'*<code>{mess}</code>*')
        else:
            await message.answer( text=f'*<code>{about_my_self}</code>*' )
        text = f'Сократите количество символов до 4000 сейчас {len( about_my_self )} '
        await message.answer( text=text )
        return
    session_maker = message.bot.data['session_maker']
    user_id = message.chat.id
    logging.info( [f'userid: {user_id}', f'Длина о себе: {len( about_my_self )}'] )
    await update_user_info( session=session_maker, user_id=user_id, about_my_self=about_my_self )
    await state.finish()
    await changing_moderation( session=session_maker, user_id=user_id )
    text = 'Вы изменили пункт "О себе"'
    kb = await edit_profile_kb()
    await edit_message( message=message, text=text, markup=kb )


#редактор фото
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
        logging.info(album)
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
        await my_profile_edit_process(callback=call)
    await call.answer()


#edit_name
async def edit_name(arg: Union[types.Message, types.CallbackQuery]):
    text = 'Напиши новое имя'
    kb = await cancel_inline_kb()
    await edit_message(message=arg, text=text, markup=kb)
    await EditOther.name_state.set()


async def edit_name_state(message: Union[types.Message, types.CallbackQuery], state:FSMContext):
    logging.info('edit_name_state')
    if isinstance(message , types.CallbackQuery):
        message = message.message
    new_name = message.text
    await state.update_data(new_name=new_name)
    text = f'Вы уверены что хотите поменять имя на {new_name} '
    kb = await yes_no_kb()
    await edit_message(message=message, text=text, markup=kb)
    logging.info('edit_name_state_cancel')

async def edit_name_confirm(message: Union[types.Message, types.CallbackQuery], state:FSMContext, callback_data:dict):
    if isinstance(message,types.CallbackQuery):
        message = message.message
    callback = callback_data['callback']
    if callback == 'yes':
        user_id = message.chat.id
        session = message.bot.data['session_maker']
        data = await state.get_data()
        new_name = data['new_name']
        await update_user_info(session=session, user_id= user_id, first_name = new_name )
        text = f'Вы успешно изменили имя теперь вас зовут {new_name}'
        kb = await edit_profile_kb()
    elif callback == 'no':
        text = f'Вы отменили изменение имени'
        kb = await edit_profile_kb()
    else:
        text = 'что-то пошло не так'
        kb = await edit_profile_kb()
    await edit_message(message=message, text=text, markup=kb)
    await state.finish()



#edit_city
async def edit_city(arg: Union[types.Message, types.CallbackQuery]):
    text = 'Напиши новый город'
    kb = await cancel_inline_kb()
    await edit_message(message=arg, text=text, markup=kb)
    await EditOther.city_state.set()


async def edit_city_state(message: Union[types.Message, types.CallbackQuery], state:FSMContext):
    if isinstance(message , types.CallbackQuery):
        message = message.message
    new_city = message.text
    check_rus_city = await checking_russian_letters(new_city)
    if check_rus_city:
        new_city = await check_city(new_city)
    else:
        text = 'Напиши город на русском языке'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        return
    if new_city:
        await state.update_data(new_city=new_city[1])
        text = f'Вы уверены что хотите поменять город на {new_city[1]} '
        kb = await yes_no_kb()
        await edit_message( message=message, text=text, markup=kb )
    else:
        text = 'Нет такого города в базе напиши еще раз'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        return
async def edit_city_confirm(message: Union[types.Message, types.CallbackQuery], state:FSMContext, callback_data:dict):
    if isinstance(message,types.CallbackQuery):
        message = message.message
    callback = callback_data['callback']
    if callback == 'yes':
        user_id = message.chat.id
        session = message.bot.data['session_maker']
        data = await state.get_data()
        new_city = data['new_city']
        await update_user_info(session=session, user_id= user_id, city = new_city )
        text = f'Вы успешно изменили свой город на {new_city}'
        kb = await edit_profile_kb()
    elif callback == 'no':
        text = f'Вы отменили изменение'
        kb = await edit_profile_kb()
    else:
        text = 'что-то пошло не так'
        kb = await edit_profile_kb()
    await edit_message(message=message, text=text, markup=kb)
    await state.finish()


#edit_practice
async def edit_practice(arg: Union[types.Message, types.CallbackQuery]):
    if isinstance(arg, types.CallbackQuery):
        arg = arg.message
    session = arg.bot.data['session_maker']
    all_user_info = await select_user(session=session, user_id=arg.chat.id)
    text = f'Напиши свои новые практики сейчас твои практики:\n' \
           f'<code>{all_user_info[0]["practices"]}</code>'
    kb = await cancel_inline_kb()
    await edit_message(message=arg, text=text, markup=kb)
    await EditOther.practice_state.set()


async def edit_practice_state(message: Union[types.Message, types.CallbackQuery], state:FSMContext):
    if isinstance(message , types.CallbackQuery):
        message = message.message
    new_practice = message.text
    await state.update_data(new_practice=new_practice)
    text = f'Вы уверены что хотите поменять практики на {new_practice} '
    kb = await yes_no_kb()
    await edit_message(message=message, text=text, markup=kb)

async def edit_practice_confirm(message: Union[types.Message, types.CallbackQuery], state:FSMContext, callback_data:dict):
    if isinstance(message,types.CallbackQuery):
        message = message.message
    callback = callback_data['callback']
    if callback == 'yes':
        user_id = message.chat.id
        session = message.bot.data['session_maker']
        data = await state.get_data()
        new_practice = data['new_practice']
        await update_user_info(session=session, user_id= user_id, practices = new_practice )
        text = f'Вы успешно изменили свои практики'
        kb = await edit_profile_kb()
    elif callback == 'no':
        text = f'Вы отменили изменение'
        kb = await edit_profile_kb()
    else:
        text = 'что-то пошло не так'
        kb = await edit_profile_kb()
    await edit_message(message=message, text=text, markup=kb)
    await state.finish()

#edit_tabu
async def edit_tabu(arg: Union[types.Message, types.CallbackQuery]):
    if isinstance(arg, types.CallbackQuery):
        arg = arg.message
    session = arg.bot.data['session_maker']
    all_user_info = await select_user(session=session, user_id=arg.chat.id)
    text = f'Напиши свои новые табу сейчас твои табу:\n' \
           f'<code>{all_user_info[0]["tabu"]}</code>'
    kb = await cancel_inline_kb()
    await edit_message(message=arg, text=text, markup=kb)
    await EditOther.tabu_state.set()


async def edit_tabu_state(message: Union[types.Message, types.CallbackQuery], state:FSMContext):
    if isinstance(message , types.CallbackQuery):
        message = message.message
    new_tabu = message.text
    await state.update_data(new_tabu=new_tabu)
    text = f'Вы уверены что хотите поменять свои табу на {new_tabu} '
    kb = await yes_no_kb()
    await edit_message(message=message, text=text, markup=kb)

async def edit_tabu_confirm(message: Union[types.Message, types.CallbackQuery], state:FSMContext, callback_data:dict):
    if isinstance(message,types.CallbackQuery):
        message = message.message
    callback = callback_data['callback']
    if callback == 'yes':
        user_id = message.chat.id
        session = message.bot.data['session_maker']
        data = await state.get_data()
        new_tabu = data['new_tabu']
        await update_user_info(session=session, user_id= user_id, tabu = new_tabu )
        text = f'Вы успешно изменили свои табу'
        kb = await edit_profile_kb()
    elif callback == 'no':
        text = f'Вы отменили изменение'
        kb = await edit_profile_kb()
    else:
        text = 'что-то пошло не так'
        kb = await edit_profile_kb()
    await edit_message(message=message, text=text, markup=kb)
    await state.finish()


#edit_date_Birthday
async def edit_birthday(arg: Union[types.Message, types.CallbackQuery]):
    if isinstance(arg, types.CallbackQuery):
        arg = arg.message
    session =arg.bot.data['session_maker']
    all_user_info = await select_user(session=session, user_id=arg.chat.id)
    birthday = all_user_info[0]["birthday"]
    correct_date = birthday.strftime("%d-%m-%Y")
    text = f'Напиши свой день рождения сейчас: {correct_date}'
    kb = await cancel_inline_kb()
    await edit_message(message=arg, text=text, markup=kb)
    await EditOther.birthday_state.set()


async def edit_birthday_state(message: Union[types.Message, types.CallbackQuery], state:FSMContext):
    if isinstance(message , types.CallbackQuery):
        message = message.message
    new_birthday = message.text
    check_date = await date_formats(new_birthday)
    if check_date:
        await state.update_data(new_birthday=new_birthday)
        text = f'Вы уверены что хотите поменять день рождение на {new_birthday} '
        kb = await yes_no_kb()
        await edit_message( message=message, text=text, markup=kb )
    else:
        text = 'Введен не правильный формат даты. Введи в формате 01-01-2000'
        kb = await cancel_inline_kb()
        await edit_message( message=message, text=text, markup=kb )
        return


async def edit_birthday_confirm(message: Union[types.Message, types.CallbackQuery], state:FSMContext, callback_data:dict):
    if isinstance(message,types.CallbackQuery):
        message = message.message
    callback = callback_data['callback']
    if callback == 'yes':
        user_id = message.chat.id
        session = message.bot.data['session_maker']
        data = await state.get_data()
        new_birthday = data['new_birthday']
        await update_user_info(session=session, user_id= user_id, birthday = new_birthday )
        text = f'Вы успешно изменили свой день рождение'
        kb = await edit_profile_kb()
    elif callback == 'no':
        text = f'Вы отменили изменение'
        kb = await edit_profile_kb()
    else:
        text = 'что-то пошло не так'
        kb = await edit_profile_kb()
    await edit_message(message=message, text=text, markup=kb)
    await state.finish()


#edit_another_city
async def edit_another_city(arg: Union[types.Message, types.CallbackQuery], state:FSMContext=None):
    if isinstance(arg, types.CallbackQuery):
        arg = arg.message
    text = f'Хочешь просматривать анкеты с другого города?'
    kb = await yes_no_kb()
    await edit_message(message=arg, text=text, markup=kb)
    await EditOther.another_city_state.set()


async def edit_another_city_confirm(message: Union[types.Message, types.CallbackQuery], state:FSMContext, callback_data:dict):
    if isinstance(message,types.CallbackQuery):
        message = message.message
    callback = callback_data['callback']
    user_id = message.chat.id
    session = message.bot.data['session_maker']
    if callback == 'yes':
        await update_user_info(session=session, user_id= user_id, partner_another_city = True )
        text = f'Теперь ты будешь видеть анкеты с другого города'
        kb = await edit_profile_kb()
    elif callback == 'no':
        await update_user_info(session=session, user_id= user_id, partner_another_city = False )
        text = f'Теперь ты не будешь видеть анкеты с другого города'
        kb = await edit_profile_kb()
    else:
        text = 'что-то пошло не так'
        kb = await edit_profile_kb()
    await edit_message(message=message, text=text, markup=kb)
    await state.finish()


# edit_online_practice
async def edit_interaction_format(arg: Union[types.Message, types.CallbackQuery], state: FSMContext = None):
    if isinstance( arg, types.CallbackQuery ):
        arg = arg.message
    text = f'Какой формат ты предпочитаешь?'
    kb = await interaction_format_button()
    await edit_message( message=arg, text=text, markup=kb )
    await EditOther.interaction_format_state.set()


async def edit_interaction_format_confirm(message: Union[types.Message, types.CallbackQuery], state: FSMContext,
                                    callback_data: dict):
    logging.info('edit_interaction_format_confirm')
    if isinstance( message, types.CallbackQuery ):
        message = message.message
    callback = callback_data['callback']
    user_id = message.chat.id
    session = message.bot.data['session_maker']
    await update_user_info( session=session, user_id=user_id, interaction_format=callback )
    if callback == 'online':
        text = f'Теперь будет показываться только онлайн анкеты'
    elif callback == 'offline':
        text = f'Теперь будет показываться только офлайн анкеты '
    else:
        text = f'Теперь будет показываться офлайн и онлайн анкеты  '
    kb = await edit_profile_kb()
    await edit_message( message=message, text=text, markup=kb )
    await state.finish()


# edit_max_min_age
async def edit_min_age(arg: Union[types.Message, types.CallbackQuery], state:FSMContext=None):
    if isinstance( arg, types.CallbackQuery ):
        arg = arg.message
    text = f'Пришли новый минимальный возраст'
    kb = await cancel_inline_kb()
    await edit_message( message=arg, text=text, markup=kb )
    await EditOther.min_age_state.set()

async def edit_max_age(arg: Union[types.Message, types.CallbackQuery], state:FSMContext):
    if isinstance(arg, types.CallbackQuery):
        arg = arg.message
    text = f'Пришли новый максимальный возраст'
    kb = await cancel_inline_kb()
    try:
        min_age = int(arg.text)
        if min_age < 18 :
            await arg.answer( text='Слишком маленький возраст, пришлите другой.' )
            return
        await state.update_data(min_age=min_age)
    except ValueError:
        await arg.answer(text='Пришлите минимальный возраст')
        return
    await arg.answer( text=text, reply_markup=kb )
    await EditOther.max_age_state.set()

async def min_max_age_confirm(arg: Union[types.Message, types.CallbackQuery], state:FSMContext):
    if isinstance(arg, types.CallbackQuery):
        arg = arg.message
    data = await state.get_data()
    try:
        max_age = int(arg.text)
        min_age = int(data['min_age'])
        if min_age > max_age:
            await arg.answer( text=f'Вы ввели минимальный возраст {min_age}, а максимальный {max_age}, '
                                       f'пожалуйста введите корректный максимальный возраст' )
            return
        else:
            user_id = arg.chat.id
            session = arg.bot.data['session_maker']
            await update_user_info( session=session, user_id=user_id, min_age=min_age, max_age=max_age)
            text = f'Минимально подходящий возраст изменен на {min_age}, максимально подходящий возраст на {max_age}'
            kb = await edit_profile_kb()
            await arg.answer( text=text, reply_markup=kb )
            await state.finish()
    except ValueError:
        await arg.answer(text='Пришлите максимальный подходящий возраст')
        return


async def edit_profile_kb_process(callback:types.CallbackQuery, callback_data:dict):
    call = callback_data['callback']
    logging.info(call)
    if call == 'edit_about_me':
        await edit_about_me(callback=callback)
    elif call == 'edit_photo':
        await edit_my_photo(call=callback, user_id=callback.message.chat.id)
    elif call == 'edit_name':
        await edit_name(arg=callback)
    elif call == 'edit_city':
        await edit_city(arg=callback)
    elif call == 'edit_practice':
        await edit_practice(arg=callback)
    elif call == 'edit_tabu':
        await edit_tabu(arg=callback)
    elif call == 'edit_date_birth':
        await edit_birthday(arg=callback)
    elif call == 'edit_another_city':
        await edit_another_city(arg=callback)
    elif call == 'edit_interaction_format':
        await edit_interaction_format(arg=callback)
    elif call == 'edit_min_max_age':
        await edit_min_age(arg=callback)
    else:
        text = 'Что то пошло не так'
        await edit_message(message=callback, text=text)


def register_edit_profile(dp:Dispatcher):
    dp.register_callback_query_handler( edit_profile_kb_process, edit_profile_cd.filter())
    dp.register_message_handler( edit_about_me_state, state=EditOther.about_me_state)
# Photo
    dp.register_callback_query_handler(scrolling_my_photo_cb, my_photos_cd.filter())
    # # dp.register_message_handler(cancel_func, text='Отмена', state=EditOther.my_photo_state)
    dp.register_callback_query_handler(cancel_inline_update, cancel_cd.filter(), state=EditOther.my_photo_state)
    #
    dp.register_message_handler(add_my_photo_state, state=EditOther.my_photo_state, content_types=types.ContentType.ANY)
#Изменение имени
    # dp.register_message_handler(edit_name, cancel_cd.filter(),state=EditOther)
    dp.register_message_handler(edit_name_state,state=EditOther.name_state)
    dp.register_callback_query_handler(edit_name_confirm, yes_no_cb_new.filter(), state=EditOther.name_state)
# Изменение города
    # dp.register_message_handler(edit_name, cancel_cd.filter(),state=EditOther)
    dp.register_message_handler( edit_city_state, state=EditOther.city_state )
    dp.register_callback_query_handler( edit_city_confirm, yes_no_cb_new.filter(), state=EditOther.city_state )
# Изменение практики
    # dp.register_message_handler(edit_name, cancel_cd.filter(),state=EditOther)
    dp.register_message_handler( edit_practice_state, state=EditOther.practice_state )
    dp.register_callback_query_handler( edit_practice_confirm, yes_no_cb_new.filter(), state=EditOther.practice_state )
# Изменение табу
    # dp.register_message_handler(edit_name, cancel_cd.filter(),state=EditOther)
    dp.register_message_handler( edit_tabu_state, state=EditOther.tabu_state)
    dp.register_callback_query_handler( edit_tabu_confirm, yes_no_cb_new.filter(), state=EditOther.tabu_state )
# Изменение день рождение
    # dp.register_message_handler(edit_name, cancel_cd.filter(),state=EditOther)
    dp.register_message_handler( edit_birthday_state, state=EditOther.birthday_state )
    dp.register_callback_query_handler( edit_birthday_confirm, yes_no_cb_new.filter(), state=EditOther.birthday_state )
# Изменение партнер с другого города
    dp.register_callback_query_handler( edit_another_city_confirm, yes_no_cb_new.filter(),
                                        state=EditOther.another_city_state )
# Изменение онлайн практик
    dp.register_callback_query_handler( edit_interaction_format_confirm, interaction_format_cb.filter(),
                                        state=EditOther.interaction_format_state )

# Изменение онлайн практик
    dp.register_message_handler(edit_max_age, state=EditOther.min_age_state)
    dp.register_message_handler(min_max_age_confirm, state=EditOther.max_age_state)
