import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.check_user import CheckUserRole, CheckModerator, CheckAdmin, CheckUserDelete, CheckUserExit, \
    CheckPaid, CheckUserModeration
from tgbot.handlers.administration import administrator_handler
from tgbot.handlers.edit_profile import register_edit_profile
from tgbot.handlers.exit_profile import exit_profile_handler
from tgbot.handlers.favorites import favorites_handler
from tgbot.handlers.main_menu import main_menu_handler
from tgbot.handlers.main_profile import main_profile_handler
from tgbot.handlers.moderation import moderator_handler
from tgbot.handlers.new_anketa import register_anketa
from tgbot.handlers.other_handlers import outher_handler
from tgbot.middlewares.album_med import AlbumMiddleware
from tgbot.handlers.hello import register_hello
from tgbot.middlewares.antiflood import ThrottlingMiddleware
from tgbot.middlewares.edit_message import ReplaceOrDeleteInlineKeyboard, \
    ReplaceOrDeleteLastMessage, None_last_message
from tgbot.middlewares.last_date_activ_day import DbMiddleware
from tgbot.models.Base_model import Base
from tgbot.models.engine import create_engine_db, get_session_maker, proceed_schemas

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(AlbumMiddleware())
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(ThrottlingMiddleware())
    # dp.setup_middleware(ReplaceOrDeleteInlineKeyboard())
    # dp.setup_middleware(ReplaceOrDeleteLastMessage())
    dp.setup_middleware(None_last_message())


def register_all_filters(dp):
    dp.filters_factory.bind(CheckUserRole)
    dp.filters_factory.bind(CheckUserExit)
    dp.filters_factory.bind(CheckUserDelete)

    dp.filters_factory.bind(CheckModerator)
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(CheckPaid)
    dp.filters_factory.bind(CheckUserModeration)


def register_all_handlers(dp):
    administrator_handler(dp)
    moderator_handler(dp)
    main_menu_handler(dp)
    exit_profile_handler(dp)
    favorites_handler(dp)
    main_profile_handler(dp)
    register_edit_profile(dp)
    register_hello(dp)
    register_anketa(dp)
    outher_handler(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML', disable_web_page_preview=True)
    dp = Dispatcher(bot, storage=storage)
    engine = create_engine_db(db_path=config.db.host,db_pass=config.db.db_pass , db_user=config.db.db_user,
                              name_db=config.db.db_name)
    session_maker = get_session_maker(engine)
    proceed_schemas(Base.metadata,engine=engine)
    bot_info = await bot.get_me()
    logger.info(f"Bot name{bot_info}")

    bot['config'] = config
    bot['session_maker'] = session_maker

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)
    await dp.bot.set_my_commands( [
        types.BotCommand( "start", "Запустить бота" ),
        types.BotCommand( "restart", "Перезапустить бота" ),

    ] )

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
