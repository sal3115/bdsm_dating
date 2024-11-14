from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile

from tgbot.filters.check_user import CheckUserRole
from tgbot.keyboards.inline import func_kb_look_pravila, func_kb_acsept_pravila, func_kb_acsept_personal_data, \
    func_kb_go_to_anketa, func_kb_davayte
from tgbot.keyboards.reply import none_kb
from tgbot.misc.states import FSM_hello
from tgbot.services.auxiliary_functions import delete_keyboard
from tgbot.services.photo_and_text import  text_dict


# начало общения
async def get_start(message: types.Message, state: FSMContext):
    kb = await func_kb_look_pravila()
    text = 'Добро пожаловать в бот знакомств по интересам.\n' \
           'Прежде чем мы продолжим посмотри правила нашего бота.'
    await message.answer(text=text, reply_markup=kb)

# показываем правила сообщества
# @dp.callback_query_handler(text='after_start')
async def community_rules(callback: types.CallbackQuery, state: FSMContext):
    text = text_dict['pravila']
    # kb = await func_kb_acsept_pravila()
    kb = await func_kb_acsept_personal_data()
    await delete_keyboard(callback, current_kb=True)
    await callback.message.answer(text=text, reply_markup=kb)
    await callback.answer()



# ловим переход к анкетированию
async def start_anketirovanie(callback: types.CallbackQuery, state: FSMContext=None):
    await delete_keyboard(callback, current_kb=True)
    text = text_dict['qw_0']
    kb = await func_kb_davayte()
    await callback.message.answer(text=text, reply_markup=kb)
    await callback.answer()


def register_hello(dp: Dispatcher):
    dp.register_message_handler(get_start, CheckUserRole(False), commands='start')
    dp.register_callback_query_handler(community_rules, text='after_start')
    # dp.register_callback_query_handler(start_anketirovanie, text='acseptPersonalData')

