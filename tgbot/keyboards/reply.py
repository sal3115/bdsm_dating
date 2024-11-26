from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

#TODO сделать фильтр на все хендлеры по статусам или попробывать прямо в sql запросе сделать
async def main_menu_kb(status_user=None):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if status_user is None:
        kb.add(KeyboardButton(text='Анкеты'))
        kb.insert(KeyboardButton(text='Лайки'))
        kb.insert(KeyboardButton(text='Изменить анкету'))
    if status_user is None or status_user == 'block_user':
        kb.insert(KeyboardButton(text='Поддержка'))
    if status_user == 'delete_user' or status_user == 'exit_user':
        kb.insert(KeyboardButton(text='Восстановить аккаунт'))
    else:
        if status_user != 'block_user':
            kb.insert(KeyboardButton(text='Скрыть/показать анкету'))
    return kb


async def moderation_main_menu_kb(admin_kb=None):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.insert(KeyboardButton(text='Верификация'))
    kb.insert(KeyboardButton(text='Жалобы'))
    # kb.insert(KeyboardButton(text='Наградить'))
    # kb.insert(KeyboardButton(text='Забрать награду'))
    # kb.insert(KeyboardButton(text='Разные ссылки'))
    kb.insert(KeyboardButton(text='Поиск по ID телеграм'))
    if admin_kb:
        kb.insert( KeyboardButton( text='Назначить модератора' ) )
        kb.insert( KeyboardButton( text='Убрать модератора' ) )
        kb.insert( KeyboardButton( text='Скачать БД' ) )
    kb.insert(KeyboardButton(text='Рассылка'))
    return kb


async def cancel_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.insert( KeyboardButton( text='Отмена' ) )
    return kb


async def none_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    return kb
