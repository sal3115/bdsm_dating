import typing

from aiogram.dispatcher.filters import BoundFilter

from tgbot.models.sql_request import select_user


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
    key = 'is_user_delete'

    def __init__(self, is_user_delete: typing.Optional[bool] = None):
        self.is_user_delete = is_user_delete

    async def check(self, obj):
        if self.is_user_delete is None:
            return False
        session_maker = obj.bot.get('session_maker')
        user_id = obj.from_user.id
        check_user_id = await select_user(session_maker, user_id)
        if len(check_user_id) > 0:
            if check_user_id[0]['status'] == 'delete_user':
                return user_id == check_user_id[0]['user_id']
        else:
            return False == self.is_user_delete

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