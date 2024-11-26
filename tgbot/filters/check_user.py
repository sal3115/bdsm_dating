import logging
import typing
from datetime import datetime

from aiogram.dispatcher.filters import BoundFilter

from tgbot.models.sql_request import select_user, select_paid, delete_paid


class CheckUserRole(BoundFilter):
    key = 'is_user'

    def __init__(self, is_user: typing.Optional[bool] = None):
        self.is_user = is_user

    async def check(self, obj):
        if self.is_user is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['status'] == 'user':
                return user_id == check_user_id[0]['user_id']
            elif check_user_id[0]['status'] == 'hidden_user':
                return user_id == check_user_id[0]['user_id']
            elif check_user_id[0]['status'] == 'ver_user':
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.is_user


class CheckUserDelete(BoundFilter):
    key = 'is_user_block'

    def __init__(self, is_user_block: typing.Optional[bool] = None):
        self.is_user_block = is_user_block

    async def check(self, obj):
        if self.is_user_block is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['status'] == 'block_user':
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.is_user_block

class CheckUserExit(BoundFilter):
    key = 'is_user_exit'

    def __init__(self, is_user_exit: typing.Optional[bool] = None):
        self.is_user_exit = is_user_exit

    async def check(self, obj):
        if self.is_user_exit is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['status'] == 'exit_user':
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.is_user_exit

class CheckModerator(BoundFilter):
    key = 'is_moderator'

    def __init__(self, is_moderator: typing.Optional[bool] = None):
        self.is_moderator = is_moderator

    async def check(self, obj):
        if self.is_moderator is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['status'] == 'moderator':
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.is_moderator



#если потребуестся проверять по БД
class CheckAdmin(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['status'] == 'admin':
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.is_admin

logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
class CheckPaid(BoundFilter):
    key = 'is_paid'
    def __init__(self, is_paid: typing.Optional[bool] = None):
        self.is_paid = is_paid
    async def check(self, obj):
        if self.is_paid is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_paid(session_maker, user_id)
        if len(check_user_id) > 0:
            today = datetime.now().date()
            if check_user_id[0]['date_before'] >= datetime.now().date():
                return user_id == check_user_id[0]['user_id']
            else:
                await delete_paid(session=session_maker, user_id=user_id)
        else:
            return False == self.is_paid




class CheckUserModeration(BoundFilter):
    key = 'check_user_in_moderation'

    def __init__(self, check_user_in_moderation: typing.Optional[bool] = None):
        self.check_user_in_moderation = check_user_in_moderation

    async def check(self, obj):
        if self.check_user_in_moderation is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['moderation'] == True:
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.check_user_in_moderation