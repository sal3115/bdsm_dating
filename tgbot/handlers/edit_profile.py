import logging
from typing import Union

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from tgbot.keyboards.inline import func_kb_back_2, func_kb_phone, new_kb_back, yes_no_button, \
    yes_no_cb
from tgbot.keyboards.reply import main_menu_kb
from tgbot.misc.states import EditProfile
from tgbot.models.sql_request import update_user_info
from tgbot.services.anketa_utulites import check_mail
from tgbot.services.auxiliary_functions import edit_message, delete_keyboard
from tgbot.services.photo_and_text import text_dict


async def complete_edit(message:Message, state:FSMContext):
    kb = await main_menu_kb()
    await edit_message(message=message, text='Редактирование завершено', markup=kb)
    await state.finish()


async def first_edit_profile(message:Union[Message, CallbackQuery], state=FSMContext):
    logging.info(f'------------------------- first_edit_profile')
    kb = await new_kb_back(button_next=True)
    text = "Здесь ты можешь отредактировать свою анкету"
    await edit_message(message=message, text= text, markup=kb)
    await EditProfile.email_state.set()

#TODO сделать везде при изменении статус пользователя False и сделать функцию отправки на модерацию
async def edit_email(message: Message, state: FSMContext):
    logging.info(f'------------------------- editing email')
    text = text_dict['qw_4']
    kb = await func_kb_phone(button_next=True, button_complete=True)
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await EditProfile.phone_state.set()
    elif await check_mail(message.text):
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await update_user_info(session= session_maker,user_id=user_id, e_mail=message.text)
        await message.answer( text=text, reply_markup=kb )
        await EditProfile.phone_state.set()
    else:
        text = text_dict['qw_3']
        kb = await new_kb_back( button_next=True )
        await message.answer( text=text, reply_markup=kb )
        await EditProfile.email_state.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()])



async def edit_phone(message:Message, state: FSMContext):
    logging.info(f'------------------------- editing phone')
    text = text_dict['qw_5']
    kb = await new_kb_back(button_next=True, button_back=True)
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer( text=text, reply_markup=kb )
    elif message.contact is not None:
        phone_number = message.contact.phone_number
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await update_user_info(session= session_maker,user_id=user_id,phone_number=phone_number )
        await message.answer( text=text, reply_markup=kb )
    else:
        pass
    await EditProfile.social_network_state.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )


async def edit_social_network(message:Message, state: FSMContext):
    logging.info(f'------------------------- editing social network')
    text = text_dict['qw_8']
    kb = await new_kb_back( button_next=True, button_back=True )
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer( text=text, reply_markup=kb )
    else:
        await message.answer( text=text, reply_markup=kb )
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        social_network = message.text
        await update_user_info(session= session_maker,user_id=user_id,social_network=social_network )
    await EditProfile.country_state.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )


async def edit_country(message:Message, state:FSMContext):
    logging.info( f'------------------------- editing country' )
    text = text_dict['qw_9']
    kb = await new_kb_back(button_next=True, button_back=True)
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer( text=text, reply_markup=kb )
    else:
        country = message.text
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await update_user_info(session= session_maker,user_id=user_id,country=country )
        await message.answer( text=text, reply_markup=kb )
    await EditProfile.city_state.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )


async def edit_city(message:Message, state:FSMContext):
    logging.info( f'------------------------- editing city' )
    text = text_dict['qw_10']
    kb = await yes_no_button( message )
    if message.text == '🔙Вернуться НАЗАД':
        await message.bot.edit_message_reply_markup( chat_id=message.chat.id, message_id=message.message_id - 1 )
        await message.answer( text=text, reply_markup=kb )
    elif message.text == 'Пропустить🔜':
        await message.answer( text=text, reply_markup=kb )
    else:
        city = message.text
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await update_user_info(session= session_maker,user_id=user_id,town=city )
        await message.answer( text=text, reply_markup=kb )
    await EditProfile.confession_state.set()
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )


async def edit_confession(arg: Union[Message, CallbackQuery], state: FSMContext):
    logging.info( f'------------------------- editing confession' )
    text = text_dict['qw_11']
    kb = await new_kb_back(button_next=True, button_back=True)
    if isinstance(arg, CallbackQuery):
        message = arg.message
        confesion_data = arg.data
        if confesion_data != 'conf_new':
            confesion_data = arg.data.split(',')
            conf = confesion_data[0]
            session_maker = arg.message.bot.data['session_maker']
            user_id = message.chat.id
            await update_user_info(session= session_maker,user_id=user_id,confession=conf)
            await message.edit_reply_markup()
            await message.answer(text=text, reply_markup=kb)
            await EditProfile.church_state.set()
        else:
            text = text_dict['qw_10_1']
            await message.edit_reply_markup()
            await message.answer(text=text, reply_markup=kb)
            await EditProfile.confession_new_state.set()
    if isinstance(arg, Message):
        if arg.text == '🔙Вернуться НАЗАД' or arg.text == 'Пропустить🔜':
            message = arg
            await message.answer(text=text, reply_markup=kb)
            await EditProfile.church_state.set()
        elif await state.get_state() == 'EditProfile:confession_state':
            await arg.delete()
        else:
            await arg.answer(text=text, reply_markup=kb)
    data = await state.get_data()
    logging.info( msg=[data, await state.get_state()] )

async def edit_new_confession(message:Message, state: FSMContext):
    logging.info( f'------------------------- editing new_confession' )
    conf = message.text
    session_maker = message.bot.data['session_maker']
    user_id = message.chat.id
    await update_user_info( session=session_maker, user_id=user_id, confession=conf )
    text = text_dict['qw_11']
    kb = await new_kb_back(button_back=True, button_next=True)
    await message.answer(text=text, reply_markup=kb)
    await EditProfile.church_state.set()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])


async def edit_church(message:Message, state:FSMContext):
    logging.info(f'------------------------- editing church')
    kb_yes = await yes_no_button()
    text = text_dict['qw_17_1']#вопрос про анкеты другого города
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb_yes)
        await EditProfile.profiles_another_city_state.set()

    else:
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await update_user_info( session=session_maker, user_id=user_id, church=message.text )
        await message.answer( text=text, reply_markup=kb_yes )

        await EditProfile.profiles_another_city_state.set()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])

async def edit_profile_other_city(message:Union[Message, CallbackQuery], state:FSMContext, callback_data: dict = None):
    logging.info(f'------------------------- editing other_city')
    text = text_dict['qw_18']#вопрос про анкеты другой страны
    kb_yes = await yes_no_button()
    if isinstance( message, Message ):
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await delete_keyboard( message )
            await message.answer( text=text, reply_markup=kb_yes )
            await EditProfile.profiles_another_country_state.set()
        else:
            await message.delete()
    else:
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await message.edit_text( text=text, reply_markup=kb_yes )
        await update_user_info( session=session_maker, user_id=user_id, partner_another_city=answer )
        await EditProfile.profiles_another_country_state.set()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])


async def edit_profile_other_country(message:Union[Message, CallbackQuery], state:FSMContext, callback_data: dict = None):
    logging.info(f'------------------------- editing other_country')
    text = text_dict['qw_19']  #вопрос про анкеты другой конфесии
    kb_yes = await yes_no_button()
    if isinstance( message, Message ):
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await delete_keyboard( message )
            await message.answer( text=text, reply_markup=kb_yes )
            await EditProfile.profiles_another_confession_state.set()
        else:
            await message.delete()
    else:
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await message.edit_text( text=text, reply_markup=kb_yes )
        await update_user_info( session=session_maker, user_id=user_id, partner_another_town = answer )
        await EditProfile.profiles_another_confession_state.set()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])

async def edit_profile_other_confession(message:Union[Message, CallbackQuery], state:FSMContext, callback_data: dict = None):
    logging.info(f'------------------------- editing other confession')
    text = text_dict['qw_20']  # вопрос про минимальный возраст
    kb = await new_kb_back()
    if isinstance( message, Message ):
        if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
            await delete_keyboard( message )
            await message.answer( text=text, reply_markup=kb )
            await EditProfile.min_age_state.set()
        else:
            await message.delete()
    else:
        message = message.message
        answer = callback_data['callback']
        if answer == 'yes':
            answer = True
        else:
            answer = False
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await message.edit_text( text=text )
        await update_user_info( session=session_maker, user_id=user_id, partner_another_conf = answer )
        await EditProfile.min_age_state.set()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])

async def edit_min_age(message:Message, state:FSMContext):
    logging.info(f'------------------------- editing min_age')
    text = text_dict['qw_21']  # вопрос про максимальный возраст
    kb = await new_kb_back(button_back=True)
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await EditProfile.max_age_state.set()
    else:
        try:
            min_age = int(message.text)
        except ValueError:
            await message.answer(text='Пришлите минимально подходящий возраст')
            return
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        await edit_message(message=message, text=text, markup=kb )
        await update_user_info( session=session_maker, user_id=user_id, min_age=min_age )
        await EditProfile.max_age_state.set()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])

async def edit_max_age(message:Message, state:FSMContext):
    logging.info(f'------------------------- editing max_age')
    text = text_dict['qw_24']  # завершающий вопрос
    kb = await new_kb_back(button_back=True)
    if message.text == '🔙Вернуться НАЗАД' or message.text == 'Пропустить🔜':
        await message.answer(text=text, reply_markup=kb)
        await state.finish()
    else:
        try:
            max_age = int(message.text)
        except ValueError:
            await message.answer(text='Пришлите максимально подходящий возраст')
            return
        session_maker = message.bot.data['session_maker']
        user_id = message.chat.id
        kb = await main_menu_kb()
        await message.answer( text=text, reply_markup=kb )
        await update_user_info( session=session_maker, user_id=user_id, max_age=max_age )
    await state.finish()
    data = await state.get_data()
    logging.info(msg=[data, await state.get_state()])

async def edit_back_button(message: Message, state: FSMContext):
    curent_state = await state.get_state()
    levels = {
        "EditProfile:phone_state": first_edit_profile,
        "EditProfile:social_network_state": edit_email,
        "EditProfile:country_state": edit_phone,
        "EditProfile:city_state": edit_social_network,
        "EditProfile:confession_state": edit_country,
        "EditProfile:church_state": edit_city,
        "EditProfile:profiles_another_city_state": edit_confession,
        "EditProfile:profiles_another_country_state": edit_church,
        "EditProfile:profiles_another_confession_state":edit_profile_other_city ,
        "EditProfile:min_age_state": edit_profile_other_country,
        "EditProfile:max_age_state":edit_profile_other_confession ,
    }
    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[curent_state]
    await current_level_function(
        message,
        state = state
    )
    print(curent_state)
#
#
async def edit_next_button(message: Message, state: FSMContext):
    curent_state = await state.get_state()
    levels = {
        "EditProfile:email_state": edit_email,
        "EditProfile:phone_state": edit_phone,
        "EditProfile:social_network_state": edit_social_network,
        "EditProfile:country_state": edit_country,
        "EditProfile:city_state": edit_city,
        "EditProfile:confession_state": edit_confession,
        "EditProfile:church_state": edit_church,
        "EditProfile:profiles_another_city_state": edit_profile_other_city,
        "EditProfile:profiles_another_country_state": edit_profile_other_country,
        "EditProfile:profiles_another_confession_state": edit_profile_other_confession,
        "EditProfile:min_age_state": edit_min_age,
        "EditProfile:max_age_state": edit_max_age,

    }
    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[curent_state]
    await current_level_function(
        message,
        state = state
    )


def register_edit_profile(dp:Dispatcher):
    dp.register_message_handler(complete_edit,text ='Завершить', state=EditProfile)
    dp.register_message_handler(edit_back_button, text='🔙Вернуться НАЗАД', state=EditProfile )
    dp.register_message_handler(edit_next_button, text='Пропустить🔜', state=EditProfile )
    dp.register_message_handler( edit_email, state=EditProfile.email_state )
    dp.register_message_handler( edit_phone, state=EditProfile.phone_state )
    dp.register_message_handler( edit_phone,content_types=ContentType.CONTACT, state=EditProfile.phone_state )

    dp.register_message_handler( edit_social_network, state=EditProfile.social_network_state )
    dp.register_message_handler( edit_country, state=EditProfile.country_state )
    dp.register_message_handler( edit_city, state=EditProfile.city_state )
    dp.register_callback_query_handler( edit_confession, state=EditProfile.confession_state )
    dp.register_message_handler( edit_new_confession, state=EditProfile.confession_new_state)

    dp.register_message_handler( edit_church, state=EditProfile.church_state)

    dp.register_message_handler( edit_profile_other_city, state=EditProfile.profiles_another_city_state)
    dp.register_callback_query_handler( edit_profile_other_city, yes_no_cb.filter(), state=EditProfile.profiles_another_city_state)

    dp.register_message_handler( edit_profile_other_country, state=EditProfile.profiles_another_country_state)
    dp.register_callback_query_handler( edit_profile_other_country, yes_no_cb.filter(),state=EditProfile.profiles_another_country_state)

    dp.register_message_handler( edit_profile_other_confession, state=EditProfile.profiles_another_confession_state)
    dp.register_callback_query_handler( edit_profile_other_confession, yes_no_cb.filter(),state=EditProfile.profiles_another_confession_state)

    dp.register_message_handler( edit_min_age, state=EditProfile.min_age_state)
    dp.register_message_handler( edit_max_age, state=EditProfile.max_age_state)

