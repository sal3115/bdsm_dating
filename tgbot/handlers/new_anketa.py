import logging
from typing import Union, List

import aiogram.utils.exceptions
from aiogram import types, Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ContentType
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline import func_kb_back_2, func_kb_phone, func_kb_gender, func_kb_confessions, yes_no_button, \
    yes_no_cb, show_recommendations, ok_recommendation
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.states import FSM_hello
from tgbot.models.sql_request import insert_users, insert_photo, update_first_photo
from tgbot.services.anketa_utulites import check_mail, checking_russian_letters
from tgbot.services.auxiliary_functions import date_formats, delete_keyboard, add_photo_func
from tgbot.services.photo_and_text import text_dict


# текст попроса про Имя
async def question_1(arg: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(arg, types.Message):
        message = arg
    else:
        message = arg.message
    text = text_dict['qw_1']
    try:
        last_mes = await message.edit_text(text=text)
    except aiogram.utils.exceptions.MessageCantBeEdited:
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await FSM_hello.answer_1.set()
    await state.update_data(photo=None, video=None, guarantor=None, partner_another_city=False, partner_another_town=False,
                            partner_another_conf=False, min_age=None, max_age=None)
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


# текст вопроса про Фамилию, ловим ответ про Имя
async def question_2(message: Message, state: FSMContext):
    print(f'------------------------- question_2')
    name = message.text
    user_id = message.from_user.id
    user_name = message.from_user.username
    text = text_dict['qw_2']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_2.set()
    else:
        await state.update_data(user_id = user_id, user_name = user_name ,name=name)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_2.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

# текст вопроса про Почту, ловим ответ про Фамилию
async def question_3(message: Message, state: FSMContext):
    print(f'------------------------- question_3')

    so_name = message.text
    text = text_dict['qw_3']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_3.set()
    else:
        await state.update_data(so_name=so_name)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_3.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


# ловим почту спрашивам про телефон
async def answer_3(message: Message, state: FSMContext):
    print(f'------------------------- answer_3')

    text = text_dict['qw_4']
    kb = await func_kb_phone()
    if message.text == '🔙Вернуться НАЗАД':
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_4.set()
    elif await check_mail(message.text):
        e_mail = message.text
        await message.answer( text=text, reply_markup=kb )
        await state.update_data(e_mail=e_mail)
        await FSM_hello.answer_4.set()
    else:
        text = text_dict['qw_3']
        await FSM_hello.answer_3.set()
        kb = await func_kb_back_2()
        await message.answer( text=text, reply_markup=kb )
        return
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


# ловим ответ на телефон и отправляем запрос по соцсетям
async def answer_4(message: Message, state: FSMContext):
    print(f'------------------------- answer_4')

    text = text_dict['qw_5']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_5.set()
    elif message.contact is not None:
        phone_number = message.contact.phone_number
        await state.update_data(phone_number=phone_number)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_5.set()
    elif message.contact is None:
        text = text_dict['qw_4']
        kb = await func_kb_phone()
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_4.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

# ловим ответ про соцсети спрашиваем пол
async def answer_5(message: Message, state: FSMContext):
    print(f'------------------------- answer_5')

    text = text_dict['qw_6']
    kb = await func_kb_gender()
    if message.text == '🔙Вернуться НАЗАД':
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_6.set()
    else:
        await message.answer(text=text, reply_markup=kb)
        social_network = message.text
        await state.update_data(social_network=social_network)
        await FSM_hello.answer_6.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

# ловим ответ про пол спрашиваем дату рождения
async def answer_6(arg: Union[Message, CallbackQuery], state: FSMContext):
    print(f'------------------------- answer_6')
    if isinstance(arg, types.CallbackQuery):
        message = arg.message
    else:
        message = arg
    text = text_dict['qw_7']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        await FSM_hello.answer_7.set()
    if message.reply_markup:
        await message.edit_reply_markup()
        gender = arg.data
        await state.update_data( gender=gender )
        await arg.answer()
        await FSM_hello.answer_7.set()
    else:
        await message.delete()
    await message.answer( text=text, reply_markup=kb )
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])



#ловим ответ про дату рождения запрос страны
async def answer_7(message: Message, state: FSMContext):
    print(f'------------------------- answer_7')
    text = text_dict['qw_8']
    kb = await func_kb_back_2()
    check_date = await date_formats(message.text)
    if message.text =='🔙Вернуться НАЗАД':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_8.set()
    elif check_date:
        await state.update_data(birthday=check_date)
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_8.set()
    else:
        text = text_dict['qw_7']
        kb = await func_kb_back_2()
        await message.answer(text=text, reply_markup=kb)
        # await FSM_hello.answer_8.set()
        return
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

#ловим страну спрашиваем город
async def answer_8(message: Message, state: FSMContext):
    print(f'------------------------- answer_8')
    text = text_dict['qw_9']
    kb = await func_kb_back_2()
    country = message.text
    if message.text == '🔙Вернуться НАЗАД':
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id-1)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_9.set()
    elif await checking_russian_letters(country):
        await state.update_data(country=country)
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_9.set()
    else:
        text = text_dict['qw_8']
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_8.set()
        return
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

#ловим город спрашиваем конфесию
async def answer_9(message: Message, state: FSMContext):
    print(f'------------------------- answer_9')
    text = text_dict['qw_10']
    kb = await func_kb_confessions( message )
    town = message.text
    if message.text == '🔙Вернуться НАЗАД':
        await FSM_hello.answer_10.set()
        await message.answer( text=text, reply_markup=kb )
    elif await checking_russian_letters(town):
        await state.update_data(town=town)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_10.set()
    else:
        text = text_dict['qw_9']
        kb = await func_kb_back_2()
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_9.set()
        return
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

# ловим выбор конфессии, задаем вопрос про название церкви
async def answer_10(arg: Union[Message, CallbackQuery], state: FSMContext):
    print(f'------------------------- answer_10')
    text = text_dict['qw_11']
    kb = await func_kb_back_2()
    if isinstance(arg, types.CallbackQuery):
        message = arg.message
        confesion_data = arg.data
        if confesion_data != 'conf_new':
            confesion_data = arg.data.split(',')
            conf_id = int(confesion_data[1])
            conf = confesion_data[0]
            await state.update_data(conf=conf)
            await message.edit_reply_markup()
            last_mes = await message.answer(text=text, reply_markup=kb)
            await FSM_hello.answer_11.set()
            data = await state.get_data()
        else:
            text = text_dict['qw_10_1']
            kb = await func_kb_back_2()
            await message.edit_reply_markup()
            last_mes = await message.answer(text=text, reply_markup=kb)
            await FSM_hello.answer_10_1.set()
            data = await state.get_data()
            logging.info( msg=[data, await state.get_state()] )
    if isinstance(arg, types.Message):
        if arg.text == '🔙Вернуться НАЗАД':
            message = arg
            await message.answer(text=text, reply_markup=kb)
            await FSM_hello.answer_11.set()
        elif await state.get_state() == 'FSM_hello:answer_10':
            await arg.delete()
        else:
            await arg.answer(text=text, reply_markup=kb)
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

# ловим ввод новой конфессии вручную
async def answer_10_1(message: Message, state: FSMContext):
    print(f'------------------------- answer_10_1')
    conf = message.text
    if len(conf) > 30:
        text = 'Слишком длинная конфессия, сократите пожалуйста'
        await message.answer(text=text)
        await FSM_hello.answer_10_1.set()
        return
    await state.update_data(conf=f'{conf}')
    text = text_dict['qw_11']
    kb = await func_kb_back_2()
    last_mes = await message.answer(text=text, reply_markup=kb)
    await FSM_hello.answer_11.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )


# ловим ввод названия церкви, о себе
async def answer_11(message: Message, state: FSMContext):
    print(f'------------------------- answer_11')
    text = text_dict['qw_12']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД':
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_12.set()
    else:
        church = message.text
        await state.update_data(church=church)
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_12.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

# ловим обо мне просим загрузить фото
async def answer_12(message: Message, state: FSMContext):
    print(f'------------------------- answer_12')
    text = text_dict['qw_13']
    kb = await func_kb_back_2( button_next=True )
    if message.text == '🔙Вернуться НАЗАД':
        last_mes = await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_13.set()
    else:
        about_me = message.text
        await state.update_data( about_me=about_me )
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_13.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


# ловим фото и загружаем фото в полный рост
async def answer_13(message: Message, state:FSMContext, album: List[types.Message]=None):
    print( 'func', 'answer_13' )
    text = text_dict['qw_14']
    kb = await func_kb_back_2( button_next=True )
    if message.photo:
        photo = message.photo
        photos = await add_photo_func(photo=photo, album=album)
        logging.info(photos)
        if len( photos ) == 1:
            async with state.proxy() as data:
                data["photo"] = photos
        elif len( photos ) > 1:
            async with state.proxy() as data:
                data["photo"]= photos
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_14.set()
    else:
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await message.answer( text=text, reply_markup=kb )
            await FSM_hello.answer_14.set()
        else:
            await message.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )
#ловим фото в полный рост спрашиваем видеовизитку

async def answer_14(message: Message, state:FSMContext, album: List[types.Message]= None):
    text = text_dict['qw_15']
    kb = await func_kb_back_2( button_next=True )
    if message.photo:
        photo = message.photo
        photos = await add_photo_func( photo=photo, album=album )
        data_photo = []
        if len( photos ) > 1:
            async with state.proxy() as data:
                if 'photo' in data:
                    data_photo= data['photo']
                    for photo in photos:
                        data_photo.append(photo)
                else:
                    for photo in photos:
                        data_photo.append(photo)
                data.update(photo=data_photo)
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_15.set()
    else:
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await message.answer( text=text, reply_markup=kb )
            await FSM_hello.answer_15.set()
        else:
            await message.delete()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


#принимаем видеовизитку спашиваем рекомендации пастора
async def answer_15(message: Message, state:FSMContext, album: List[types.Message]= None):
    print( 'func', 'answer_15' )
    text = text_dict['qw_16']
    kb = await show_recommendations()
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_16.set()
        return
    elif not message.video and not message.video_note:
        await message.delete()
        return
    elif message.video:
        video = message.video.file_id
    elif message.video_note:
        video = message.video_note.file_id
    await state.update_data(video=video)
    await message.answer( text=text, reply_markup=kb )
    await FSM_hello.answer_16.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

async def answer_15_1(call: CallbackQuery, state:FSMContext):
    data = await state.get_data()
    text = text_dict['qw_16_1'].format(data['so_name'],data['name'], data['user_id'])
    await call.message.edit_reply_markup()
    kb = await ok_recommendation()
    await call.message.answer(text=text, reply_markup=kb)
    await FSM_hello.answer_16_1.set()
    logging.info( msg=[data, await state.get_state()])
    await call.answer()


#принимаем рекомендации пастора спашиваем анкеты другого города
async def answer_16(message: Union[Message, CallbackQuery], state:FSMContext, album: List[types.Message]= None):
    print( 'func', 'answer_16' )
    text = text_dict['qw_17']
    kb_yes = await yes_no_button()
    if isinstance(message, CallbackQuery):
        message = message.message
        await message.edit_reply_markup()
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await delete_keyboard( message )
        await message.answer(text=text, reply_markup=kb_yes) # TODO придумать как убрать "пропустить"
        await FSM_hello.answer_17.set()
    else:
        await message.answer(text=text, reply_markup=kb_yes)
        await FSM_hello.answer_17.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])


#принимаем анкеты другого города спашиваем анкеты другой страны
async def answer_17(message: Union[Message, CallbackQuery], state:FSMContext, callback_data: dict = None):
    print( 'func', 'answer_17' )
    text = text_dict['qw_18']
    kb_yes = await yes_no_button()
    if isinstance(message, types.Message):
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await delete_keyboard(message)
            await message.answer(text=text, reply_markup=kb_yes)
            await FSM_hello.answer_18.set()
        else:
            await message.delete()
    else:
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        await state.update_data(partner_another_city=answer)
        await message.edit_text( text=text, reply_markup=kb_yes )
        await FSM_hello.answer_18.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

#принимаем анкеты другой страны спашиваем анкеты другой конфессии
async def answer_18(message: Union[types.Message, types.CallbackQuery], state:FSMContext,callback_data: dict = None):
    print( 'func', 'answer_18' )
    text = text_dict['qw_19']
    kb_yes = await yes_no_button()
    if isinstance(message, types.Message):
        message = message
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await delete_keyboard(message)
            last_mes = await message.answer(text=text, reply_markup=kb_yes)
            await FSM_hello.answer_19.set()
    else:
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        await state.update_data(partner_another_town=answer)
        await message.edit_text(text=text, reply_markup=kb_yes)
        await FSM_hello.answer_19.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

#принимаем анкеты другой конфессии спашиваем Минимальный подходящий возраст
async def answer_19(message: Union[types.Message, types.CallbackQuery], state:FSMContext,callback_data: dict = None):
    print( 'func', 'answer_19' )
    text = text_dict['qw_20']
    kb = await func_kb_back_2()
    if isinstance(message, types.Message):
        message = message
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await delete_keyboard(message)
            await message.answer(text=text)
            await FSM_hello.answer_20.set()
    else:
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        await state.update_data(partner_another_conf=answer)
        await message.edit_reply_markup()
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_20.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

#принимаем Минимальный подходящий возраст спашиваем максимальный подходящий возраст
async def answer_20(message: Message, state:FSMContext):
    print( 'func', 'answer_20' )
    text = text_dict['qw_21']
    kb = await func_kb_back_2()
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await FSM_hello.answer_21.set()
    else:
        try:
            min_age = int(message.text)
            await state.update_data(min_age=min_age)
        except ValueError:
            await message.answer(text='Пришлите минимально подходящий возраст')
            return
        await message.answer( text=text, reply_markup=kb )
        await FSM_hello.answer_21.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])

#принимаем максимальный подходящий возраст  завершающий этап
async def answer_21(message: Message, state:FSMContext, album: List[types.Message]= None):
    print( 'func', 'answer_21' )
    text = text_dict['qw_22']
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer( text=text)
        await FSM_hello.answer_22.set()
        data = await state.get_data()
        logging.info( msg=[data, await state.get_state()])
    else:
        try:
            max_age = int(message.text)
            await state.update_data(max_age=max_age)
        except ValueError:
            await message.answer(text='Пришлите максимально подходящий возраст')
            return
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
        kb = await main_menu_kb()
        await state.finish()
        await message.answer( text=text, reply_markup=kb )




async def back_button(message: Message, state: FSMContext):
    curent_state = await state.get_state()
    levels = {
        "FSM_hello:answer_2": question_1,
        "FSM_hello:answer_3": question_2,
        "FSM_hello:answer_4": question_3,
        "FSM_hello:answer_5": answer_3,
        "FSM_hello:answer_6": answer_4,
        "FSM_hello:answer_7": answer_5,
        "FSM_hello:answer_8": answer_6,
        "FSM_hello:answer_9": answer_7,
        "FSM_hello:answer_10": answer_8,
        "FSM_hello:answer_10_1": answer_9,
        "FSM_hello:answer_11": answer_9,
        "FSM_hello:answer_12": answer_10,
        "FSM_hello:answer_13": answer_11,
        "FSM_hello:answer_14": answer_12,
        "FSM_hello:answer_15": answer_13,
        "FSM_hello:answer_16": answer_14,
        "FSM_hello:answer_16_1": answer_15,
        "FSM_hello:answer_17": answer_15,
        "FSM_hello:answer_18": answer_16,
        "FSM_hello:answer_19": answer_17,
        "FSM_hello:answer_20": answer_18,
        "FSM_hello:answer_21": answer_19,

    }
    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[curent_state]
    await current_level_function(
        message,
        state = state
    )
    print(curent_state)


async def next_button(message: Message, state: FSMContext):
    curent_state = await state.get_state()
    levels = {
        "FSM_hello:answer_13": answer_13,
        "FSM_hello:answer_14": answer_14,
        "FSM_hello:answer_15": answer_15,
        "FSM_hello:answer_16": answer_16,
        "FSM_hello:answer_16_1": answer_16,
        "FSM_hello:answer_17": answer_17,
        "FSM_hello:answer_18": answer_18,
        "FSM_hello:answer_19": answer_19,
        "FSM_hello:answer_20": answer_20,

    }
    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[curent_state]
    await current_level_function(
        message,
        state = state
    )



def register_anketa(dp:Dispatcher):
    dp.register_message_handler(back_button, text='🔙Вернуться НАЗАД', state=FSM_hello )
    dp.register_message_handler(next_button, text='Пропустить🔜', state=FSM_hello )
    dp.register_callback_query_handler( question_1, text='davayte', state=FSM_hello.qw_0 )
    dp.register_message_handler( question_2, state=FSM_hello.answer_1 )
    dp.register_message_handler( question_3, state=FSM_hello.answer_2)
    dp.register_message_handler( answer_3,  state=FSM_hello.answer_3 )
    dp.register_message_handler( answer_4, content_types=ContentType.CONTACT, state=FSM_hello.answer_4 )
    dp.register_message_handler( answer_4, state=FSM_hello.answer_4 )
    dp.register_message_handler( answer_5, state=FSM_hello.answer_5  )
    dp.register_callback_query_handler( answer_6, text='men', state=FSM_hello.answer_6  )
    dp.register_callback_query_handler( answer_6, text='women', state=FSM_hello.answer_6 )
    dp.register_message_handler( answer_6, state=FSM_hello.answer_6 )
    dp.register_message_handler( answer_7,  state=FSM_hello.answer_7  )
    dp.register_message_handler( answer_8, state=FSM_hello.answer_8  )
    dp.register_message_handler( answer_9, state=FSM_hello.answer_9 )
    dp.register_callback_query_handler( answer_10, state=FSM_hello.answer_10 )
    dp.register_message_handler( answer_10, state=FSM_hello.answer_10 )
    dp.register_message_handler( answer_10_1, state=FSM_hello.answer_10_1)
    dp.register_message_handler( answer_11, state=FSM_hello.answer_11  )
    dp.register_message_handler( answer_12, state=FSM_hello.answer_12  )
    dp.register_message_handler( answer_13, state=FSM_hello.answer_13, content_types=types.ContentType.ANY)
    dp.register_message_handler( answer_14, state=FSM_hello.answer_14, content_types=types.ContentType.ANY)
    dp.register_message_handler( answer_15, state=FSM_hello.answer_15, content_types=types.ContentType.ANY  )
    dp.register_callback_query_handler( answer_15_1, state=FSM_hello.answer_16)
    dp.register_callback_query_handler( answer_16, state=FSM_hello.answer_16_1)
    dp.register_message_handler( answer_16, state=FSM_hello.answer_16)
    dp.register_message_handler( answer_17, state=FSM_hello.answer_17)
    dp.register_callback_query_handler( answer_17, yes_no_cb.filter() , state=FSM_hello.answer_17 )
    dp.register_message_handler( answer_18, state=FSM_hello.answer_18  )
    dp.register_callback_query_handler( answer_18, yes_no_cb.filter() , state=FSM_hello.answer_18 )
    dp.register_message_handler( answer_19, state=FSM_hello.answer_19  )
    dp.register_callback_query_handler( answer_19, yes_no_cb.filter() , state=FSM_hello.answer_19 )
    dp.register_message_handler( answer_20, state=FSM_hello.answer_20  )
    dp.register_message_handler( answer_21, state=FSM_hello.answer_21 )






