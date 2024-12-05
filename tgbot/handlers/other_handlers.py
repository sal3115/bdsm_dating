from aiogram import types, Dispatcher
from aiogram.types import ContentType

from tgbot.keyboards.reply import main_menu_kb
from tgbot.models.sql_request import select_user
from tgbot.services.auxiliary_functions import edit_message


async def raw_message(message: types.Message):
    await message.delete()

async def first_page_other(message:types.Message):
    session = message.bot.data['session_maker']
    user_id = message.from_user.id
    info_user = await select_user(session=session, user_id=user_id)
    status_user = info_user[0]['status']
    if status_user == 'delete_user':
        text = 'Вы удалили свой аккаунт, но вы всегда можете его восстановить'
        kb = await main_menu_kb(status_user='delete_user')
        await edit_message(message=message, text=text, markup=kb)
    elif status_user =='exit_user':
        text = 'Вы вышли из аккаунта.'
        kb = await main_menu_kb( status_user='exit_user' )
        await edit_message( message=message, text=text, markup=kb )
    elif status_user =='block':
        text = f'Вы заблокированы администрацией. Если это произошло по ошибке, обратитесь к администрации сервиса '
        await edit_message( message=message, text=text)
    else:
        return
def outher_handler(dp:Dispatcher):
    dp.register_message_handler(first_page_other, commands='start')
    dp.register_message_handler( raw_message, content_types=ContentType.ANY ,state='*' )

