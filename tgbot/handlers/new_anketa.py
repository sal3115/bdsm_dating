import datetime
import logging
from typing import Union, List

import aiogram.utils.exceptions
from aiogram import types, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline import func_kb_back_2, func_kb_gender, yes_no_button, \
    func_kb_position, yes_no_cb, interaction_format_button, interaction_format_cb, yes_no_kb_confirm_city, \
    yes_no_cb_confirm_city
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.states import FSM_hello
from tgbot.models.sql_request import insert_users, insert_photo, update_first_photo
from tgbot.services.anketa_utulites import checking_russian_letters
from tgbot.services.auxiliary_functions import date_formats, add_photo_func, check_city
from tgbot.services.calculate_age import calculateAge
from tgbot.services.photo_and_text import text_dict


# текст попроса про Имя
async def your_name(arg: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(arg, types.Message):
        message = arg
    else:
        message = arg.message
    text = text_dict['qw_1']
    try:
        await message.edit_text(text=text)
    except aiogram.utils.exceptions.MessageCantBeEdited:
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await FSM_hello.your_name.set()
    user_name = message.chat.username
    user_id = message.chat.id
    await state.update_data(user_id=user_id, user_name=user_name, photo=None, partner_another_city=False,
                             min_age=None, max_age=None, gender_partner = None)
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим ответ про имя спрашиваем пол
async def name_gender(message: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(message, CallbackQuery):
        message = message.message
    text = text_dict['qw_6']
    kb = await func_kb_gender()
    if message.text == '🔙Вернуться НАЗАД':
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_gender.set()
    else:
        await message.answer(text=text, reply_markup=kb)
        if message.reply_markup:
            await FSM_hello.your_gender.set()
            return
        your_name = message.text
        await state.update_data(name=your_name)
        await FSM_hello.your_gender.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим ответ про пол спрашиваем дату рождения
async def gender_choice_partner(arg: Union[Message, CallbackQuery], state: FSMContext):
    data = await state.get_data()
    if isinstance(arg, types.CallbackQuery):
        message = arg.message
    else:
        message = arg
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        gender = data['gender']
        kb = await func_kb_gender( gender=gender )
        text = text_dict['qw_6_1']
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.choice_partner.set()
    if message.reply_markup:
        await message.edit_reply_markup()
        gender = arg.data
        if gender == 'men':
            await FSM_hello.choice_partner.set()
            text = text_dict['qw_6_1']
            kb = await func_kb_gender(gender='men')
            await state.update_data( gender=gender )
            await message.answer( text=text, reply_markup=kb )
        elif gender == 'women':
            await FSM_hello.choice_partner.set()
            text = text_dict['qw_6_1']
            kb = await func_kb_gender()
            await state.update_data( gender=gender )
            await message.answer( text=text, reply_markup=kb )
        elif gender == 'pair':
            await FSM_hello.choice_partner.set()
            text = text_dict['qw_6_1']
            kb = await func_kb_gender()
            await state.update_data( gender=gender )
            await message.answer( text=text, reply_markup=kb )
        elif gender == 'back':
            await FSM_hello.your_name.set()
            await your_name(arg=arg, state=state)
        await arg.answer()
    else:
        await message.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

async def choice_partner_date_of_birth(arg: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(arg, types.CallbackQuery):
        message = arg.message
    else:
        message = arg
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        text = text_dict['qw_7']
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_date_of_birth.set()
    if message.reply_markup:
        gender_partner = arg.data
        if gender_partner == 'back':
            await message.edit_reply_markup()
            await arg.answer()
            await name_gender(message=arg, state=state)
        else:
            await message.edit_reply_markup()
            await state.update_data( gender_partner=gender_partner )
            await FSM_hello.your_date_of_birth.set()
            text = text_dict['qw_7']
            await message.answer( text=text, reply_markup=kb )
            await arg.answer()
    else:
        await message.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


#ловим ответ про дату рождения запрос города
async def birth_city(message: Message, state: FSMContext):
    text = text_dict['qw_9']
    kb = await func_kb_back_2()
    check_date = await date_formats(message.text)
    if message.text =='🔙Вернуться НАЗАД':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.your_city.set()
    elif check_date:
        age = await calculateAge(check_date)
        if age >= 18:
            await state.update_data(birthday=check_date)
            await message.answer(text=text, reply_markup=kb)
            await FSM_hello.your_city.set()
        else:
            text = '❗️❗️❗️❗️Заполнение анкеты прервано, вам нет 18 лет, просьба покинуть ресурс❗️❗️❗️❗️'
            await message.answer( text=text, reply_markup=None )
            await state.finish()
            return
    else: # запрос даты рождения
        text = text_dict['qw_7']
        kb = await func_kb_back_2()
        await message.answer(text=text, reply_markup=kb)
        return
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
#ловим город спрашиваем позиция в теме
async def city_city_confirm(message: Message, state: FSMContext):
    city = message.text
    check_rus_city = await checking_russian_letters( city )
    if check_rus_city:
        city = await check_city( city )
    else:
        text = text_dict['qw_9_1']  # спрашиваем город русскими буквами
        kb = await func_kb_back_2()
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_city.set()
        return
    if city:
        await state.update_data( city=city[1] )
        text = text_dict['qw_9_3'].format(city[1])
        kb = await yes_no_kb_confirm_city()
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_city_confirm.set()
    else:
        text = text_dict['qw_9_2'] # нет города в базе
        kb = await func_kb_back_2()
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.your_city.set()
        return
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим выбор позиции, задаем вопрос позицию партнера

async def city_confirm_position(callback: Union[types.CallbackQuery, types.CallbackQuery], state:FSMContext, callback_data:dict=None):
    text = text_dict['qw_10']
    kb = await func_kb_position()
    if isinstance(callback, types.Message):
        await FSM_hello.your_position.set()
        await callback.answer( text=text, reply_markup=kb )
        return
    call = callback_data['callback']
    if call == 'yes':
        await callback.message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_position.set()
        await callback.answer()
        await callback.message.edit_reply_markup()
    elif call == 'no':
        text = text_dict['qw_9']
        kb = await func_kb_back_2()
        await callback.message.answer(text=text, reply_markup=kb)
        await state.update_data( city=None )
        await FSM_hello.your_city.set()
        await callback.answer()
        await callback.message.edit_reply_markup()
    else:
        text = 'Что-то пошло не так пришлите город еще раз'



async def position_partner_position(arg: Union[Message, CallbackQuery], state: FSMContext):
    text = text_dict['qw_11'] # кого вы ищите
    kb = await func_kb_back_2()
    if isinstance(arg, types.CallbackQuery): # если нажали кнопку
        message = arg.message
        your_position = arg.data
        await state.update_data(your_position=your_position)
        await arg.message.edit_text(text=your_position, reply_markup=None)
        kb = await func_kb_position(your_position=your_position)
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.partner_position.set()
        await arg.answer()
    if isinstance(arg, types.Message):
        if arg.text == '🔙Вернуться НАЗАД':
            data = await state.get_data()
            your_position = data['your_position']
            kb = await func_kb_position( your_position=your_position )
            await arg.answer( text=text, reply_markup=kb )
            await FSM_hello.partner_position.set()
        else:
            await arg.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим позицию партнера, практики
async def partner_position_practice(arg: Union[Message, CallbackQuery], state: FSMContext):
    text = text_dict['qw_12'] #какие практики предпочитаешь
    kb = await func_kb_back_2()
    if isinstance( arg, types.CallbackQuery ):  # если нажали кнопку
        message = arg.message
        partner_position = arg.data
        await arg.message.edit_text(text=partner_position, reply_markup=None)
        await state.update_data( partner_position=partner_position )
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_practice.set()
        await arg.answer()
    if isinstance( arg, types.Message ):
        if arg.text == '🔙Вернуться НАЗАД':
            message = arg
            await message.answer( text=text, reply_markup=kb )
            await FSM_hello.your_practice.set()
        else:
            await arg.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )
# ловим практики просим табу
async def practice_tabu(message: Message, state: FSMContext):
    text = text_dict['qw_13']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        last_mes = await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_tabu.set()
    else:
        practice = message.text
        await state.update_data( practice=practice )
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_tabu.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим табу просим о себе
async def tabu_about_me(message: Message, state: FSMContext):
    text = text_dict['qw_15']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        last_mes = await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_about_me.set()
    else:
        tabu = message.text
        await state.update_data( tabu=tabu )
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_about_me.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим обо мне просим загрузить фото
async def about_me_photo(message: Message, state: FSMContext):
    text = text_dict['qw_14']
    kb = await func_kb_back_2( button_next=True )
    if message.text == '🔙Вернуться НАЗАД':
        last_mes = await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_photo.set()
    else:
        about_me = message.text
        await state.update_data( about_me=about_me )
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.your_photo.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
# ловим фото и спрашиваем мин возраст
async def photo_min_age(message: Message, state:FSMContext, album: List[types.Message]=None):
    text = text_dict['qw_20']
    kb = await func_kb_back_2()
    if message.photo:
        photo = message.photo
        photos = await add_photo_func(photo=photo, album=album)
        logging.info(album)
        if len( photos ) == 1:
            async with state.proxy() as data:
                data["photo"] = photos
        elif len( photos ) > 1:
            async with state.proxy() as data:
                data["photo"]= photos
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.min_age.set()
    else:
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await message.answer( text=text, reply_markup=kb )
            await FSM_hello.min_age.set()
        else:
            await message.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )
#принимаем Минимальный подходящий возраст спашиваем максимальный подходящий возраст
async def min_age_max_age(message: Message, state:FSMContext):
    text = text_dict['qw_21']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.max_age.set()
    else:
        try:
            min_age = int(message.text)
            if min_age < 18 :
                await message.answer( text='Слишком маленький возраст, пришлите другой.' )
                return
            await state.update_data(min_age=min_age)
        except ValueError:
            await message.answer(text='Пришлите минимально подходящий возраст')
            return
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.max_age.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])
#принимаем максимальный подходящий возраст спрашиваем анкеты других городов
async def max_age_another_city(message: Message, state:FSMContext):
    text = text_dict['qw_17_1']
    kb = await yes_no_button()
    data = await state.get_data()
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.another_city.set()
    else:
        try:
            max_age = int(message.text)
            min_age = int(data['min_age'])
            if min_age > max_age:
                await message.answer( text=f'Вы ввели минимальный возраст {min_age}, а максимальный - {max_age}, '
                                           f'пожалуйста, введите корректный максимальный возраст' )
                return
            else:
                await state.update_data(max_age=max_age)
        except ValueError:
            await message.answer(text='Пришлите максимально подходящий возраст')
            return
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.another_city.set()
    logging.info( msg=[data, await state.get_state()])


#принимаем анкеты других городов, запрос онлайн практик

async def another_city_interaction_format(message: Union[types.Message, types.CallbackQuery], state:FSMContext,
                              callback_data: dict = None, album: List[types.Message]= None):
    text = text_dict['qw_17_2']
    kb = await interaction_format_button()
    if isinstance(message, types.Message):
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await message.answer( text=text)
            await FSM_hello.interaction_format.set()
            data = await state.get_data()
            logging.info( msg=[data, await state.get_state()])
        else:
            await message.delete()
            return
    else:
        await message.answer()
        message
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        await state.update_data(partner_another_city=answer)
        await message.answer( text=text, reply_markup=kb )
        await message.edit_reply_markup()
        await FSM_hello.interaction_format.set()

    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )

#принимаем онлайн практики городов  завершающий этап
async def interaction_format_finish(message: Union[types.Message, types.CallbackQuery], state:FSMContext,
                              callback_data: dict = None, album: List[types.Message]= None):
    text = text_dict['qw_22']
    if isinstance(message, types.Message):
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await message.answer( text=text)
            await FSM_hello.finish.set()
            data = await state.get_data()
            logging.info( msg=[data, await state.get_state()])
        else:
            await message.delete()
            return
    else:
        await message.answer()
        message = message.message
        answer = callback_data['callback']
        await state.update_data(interaction_format=answer)
        data = await state.get_data()
        session = message.bot.data['session_maker']
        await insert_users(session, data)
        user_id = message.chat.id
        if data['photo'] is not None:
            photos = data['photo']
            if len(photos)>0:
                if len(photos) == 1:
                    logging.info(len(photos))
                    logging.info(photos)
                    file_id = photos[0]['file_id']
                    unique_id = photos[0]['unique_id']
                    await insert_photo( session=session, user_id=user_id, photo_id=file_id, unique_id=unique_id )
                else:
                    logging.info(len(data['photo']))
                    for photo in photos:
                        file_id = photo['file_id']
                        unique_id = photo['unique_id']
                        await insert_photo( session=session, user_id=user_id, photo_id=file_id,
                                            unique_id=unique_id )
                await update_first_photo(session=session, user_id=user_id, photo_id=photos[0]['file_id'])
        await message.edit_reply_markup()
        kb = await main_menu_kb()
        await state.finish()
        await message.answer( text=text, reply_markup=kb )
async def back_button(message: Message, state: FSMContext):
    curent_state = await state.get_state()
    logging.info(curent_state)
    data = await state.get_data()
    levels = {
        "FSM_hello:your_gender": your_name,
        "FSM_hello:your_date_of_birth": gender_choice_partner,
        "FSM_hello:your_city": choice_partner_date_of_birth,
        'FSM_hello:your_city_confirm': birth_city,
        "FSM_hello:woman_woman": name_gender,
        "FSM_hello:your_position": birth_city,
        "FSM_hello:partner_position": city_confirm_position,
        "FSM_hello:your_practice": position_partner_position,
        "FSM_hello:your_tabu": partner_position_practice,
        "FSM_hello:your_about_me": practice_tabu,
        "FSM_hello:your_photo": tabu_about_me,
        "FSM_hello:min_age": about_me_photo,
        "FSM_hello:max_age": photo_min_age,
        "FSM_hello:another_city": min_age_max_age,
        "FSM_hello:online_practice": max_age_another_city,
        "FSM_hello:finish": another_city_interaction_format,
    }
    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[curent_state]
    await current_level_function(
        message,
        state = state
    )


# async def next_button(message: Message, state: FSMContext):
#     curent_state = await state.get_state()
#     levels = {
#         "FSM_hello:answer_13": answer_13,
#         "FSM_hello:answer_14": answer_14,
#         "FSM_hello:answer_15": answer_15,
#         "FSM_hello:answer_16": answer_16,
#         "FSM_hello:answer_16_1": answer_16,
#         "FSM_hello:answer_17": answer_17,
#         "FSM_hello:answer_18": answer_18,
#         "FSM_hello:answer_19": answer_19,
#         "FSM_hello:answer_20": answer_20,
#
#     }
#     # Забираем нужную функцию для выбранного уровня
#     current_level_function = levels[curent_state]
#     await current_level_function(
#         message,
#         state = state
#     )



def register_anketa(dp:Dispatcher):
    dp.register_message_handler(back_button, text='🔙Вернуться НАЗАД', state=FSM_hello )
    # dp.register_message_handler(next_button, text='Пропустить🔜', state=FSM_hello )
    dp.register_callback_query_handler( your_name, text='acseptPersonalData')
    dp.register_callback_query_handler( your_name, state=FSM_hello.your_name, text = 'back')
    dp.register_message_handler( name_gender, state=FSM_hello.your_name )
    dp.register_callback_query_handler( gender_choice_partner, state=FSM_hello.your_gender)
    dp.register_callback_query_handler(choice_partner_date_of_birth, state=FSM_hello.choice_partner)
    dp.register_message_handler( birth_city,  state=FSM_hello.your_date_of_birth )

    dp.register_message_handler( city_city_confirm, state=FSM_hello.your_city )
    dp.register_callback_query_handler(city_confirm_position, yes_no_cb_confirm_city.filter(), state=FSM_hello.your_city_confirm)

    dp.register_message_handler( position_partner_position, state=FSM_hello.your_position  )
    dp.register_callback_query_handler( position_partner_position, state=FSM_hello.your_position  )
    dp.register_message_handler( partner_position_practice, state=FSM_hello.partner_position )
    dp.register_callback_query_handler( partner_position_practice, state=FSM_hello.partner_position )
    dp.register_message_handler( practice_tabu, state=FSM_hello.your_practice )
    dp.register_message_handler( tabu_about_me,  state=FSM_hello.your_tabu  )
    dp.register_message_handler( about_me_photo, state=FSM_hello.your_about_me  )
    dp.register_message_handler( photo_min_age, state=FSM_hello.your_photo, content_types=types.ContentType.ANY)
    dp.register_message_handler( min_age_max_age, state=FSM_hello.min_age)
    dp.register_message_handler( max_age_another_city, state=FSM_hello.max_age)
    dp.register_callback_query_handler( another_city_interaction_format, yes_no_cb.filter(), state=FSM_hello.another_city)
    dp.register_callback_query_handler(interaction_format_finish, interaction_format_cb.filter(), state= FSM_hello.interaction_format)
    dp.register_message_handler( interaction_format_finish, state=FSM_hello.interaction_format)






