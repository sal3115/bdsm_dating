from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile

from tgbot.filters.check_user import CheckUserRole
from tgbot.keyboards.inline import func_kb_look_pravila, func_kb_acsept_pravila, func_kb_acsept_personal_data, \
    func_kb_go_to_anketa, func_kb_davayte
from tgbot.misc.states import FSM_hello
from tgbot.services.auxiliary_functions import delete_keyboard
from tgbot.services.photo_and_text import video_dict, text_dict


# начало общения
async def get_start(message: types.Message, state: FSMContext):
    kb = await func_kb_look_pravila()
    video_path = video_dict['video_family']
    video = InputFile(video_path)
    await message.answer_video(video=video, caption=text_dict['text_family'],
                                          reply_markup=kb)

# показываем правила сообщества
# @dp.callback_query_handler(text='after_start')
async def community_rules(callback: types.CallbackQuery, state: FSMContext):
    text = text_dict['pravila']
    kb = await func_kb_acsept_pravila()
    await delete_keyboard(callback, current_kb=True)
    await callback.message.answer(text=text, reply_markup=kb)
    await callback.answer()


# показываем согласие на обработку данных
async def accept_rules(callback: types.CallbackQuery, state: FSMContext):
    await delete_keyboard(callback, current_kb=True)
    text = text_dict['acsept']
    kb = await func_kb_acsept_personal_data()
    await callback.message.answer(text=text, reply_markup=kb)
    if callback.message.chat.username is None:
        await FSM_hello.noUserName.set()
    else:
        await FSM_hello.yesUserName.set()
    await callback.answer()

#  ловим юзеров у которых нет юзернайма
async def user_whom_no_have_username(callback: types.CallbackQuery, state: FSMContext=None):
    if callback.message.chat.username is None:
        text = text_dict['userName_instructions']
        kb = await func_kb_go_to_anketa()
        await callback.message.answer(text=text, reply_markup=kb)
    else:
        await FSM_hello.yesUserName.set()
    await callback.answer()




# ловим переход к анкетированию
async def start_anketirovanie(callback: types.CallbackQuery, state: FSMContext=None):
    await delete_keyboard(callback, current_kb=True)
    text = text_dict['qw_0']
    kb = await func_kb_davayte()
    await callback.message.answer(text=text, reply_markup=kb)
    await FSM_hello.qw_0.set()
    await callback.answer()

async def no_user_name_go_to_anketa(call:types.CallbackQuery, state:FSMContext):
    if call.message.chat.username is None:
        await user_whom_no_have_username(callback=call)
    else:
        await start_anketirovanie(callback=call)
        await call.answer()

# ловим id фото

def register_hello(dp: Dispatcher):
    dp.register_message_handler(get_start, CheckUserRole(False), commands='start')
    dp.register_callback_query_handler(community_rules, text='after_start')
    dp.register_callback_query_handler(accept_rules, text='acseptPravila')
    dp.register_callback_query_handler(user_whom_no_have_username, text='acseptPersonalData', state=FSM_hello.noUserName)
    # dp.register_callback_query_handler(user_whom_no_have_username, text='goToAnketa', state=FSM_hello.noUserName)

    dp.register_callback_query_handler(no_user_name_go_to_anketa,text='goToAnketa' ,state=FSM_hello.noUserName)

    dp.register_callback_query_handler(start_anketirovanie, text='acseptPersonalData', state=FSM_hello.yesUserName)
    dp.register_callback_query_handler(start_anketirovanie, text='goToAnketa', state=FSM_hello.yesUserName)
    dp.register_callback_query_handler(start_anketirovanie, text='goToAnketa', state=FSM_hello.yesUserName)

