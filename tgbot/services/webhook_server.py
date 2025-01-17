import asyncio
import hashlib
import hmac
import logging
from aiohttp import web

from tgbot.config import load_config
from tgbot.models.sql_request import insert_paid_subscription, select_price_subscription_from_id

logger = logging.getLogger(__name__)

# Конфигурация
RATE_LIMIT = 10  # Максимум запросов с одного IP в минуту
request_counter = {}
async def on_startup(app):
    """Действия при запуске приложения."""
    logger.info("Webhook server started")

async def on_cleanup(app):
    """Действия при завершении работы приложения."""
    bot = app["bot"]
    await bot.session.close()
    logger.info("Webhook server stopped")
# async def validate_request(request: web.Request):
#     """Проверка подлинности уведомления."""
#     data = await request.post()  # Получаем данные из POST-запроса
#     sha1_hash = data.get("sha1_hash")
#     if not sha1_hash:
#         return False
#     config = load_config( ".env" )
#     secret_str = config.yoomoney.secret_word_yoomoney
#     # Формируем строку для проверки
#     string_to_hash = f"{data.get('notification_type')}&{data.get('operation_id')}&{data.get('amount')}&" \
#                      f"{data.get('currency')}&{data.get('datetime')}&{data.get('sender')}&{data.get('codepro')}&" \
#                      f"{secret_str}&{data.get('label')}"
#     # Вычисляем SHA1
#     generated_hash = hmac.new(
#         key=secret_str.encode(),
#         msg=string_to_hash.encode(),
#         digestmod=hashlib.sha1
#     ).hexdigest()
#     return hmac.compare_digest(generated_hash, sha1_hash)

async def validate_request(request: web.Request):
    """Проверка подлинности уведомления."""
    webhook_answer = await request.post()
    sha1_hash = webhook_answer.get("sha1_hash")
    if not sha1_hash:
        return False
    config = load_config( ".env" )
    secret_str = config.yoomoney.secret_word_yoomoney
    # Формируем строку для проверки
    str_in_hash = str(
        f'{webhook_answer["notification_type"]}&{webhook_answer["operation_id"]}&{webhook_answer["amount"]}&'
        f'{webhook_answer["currency"]}&{webhook_answer["datetime"]}&{webhook_answer["sender"]}&'
        f'{webhook_answer["codepro"]}&{secret_str}&{webhook_answer["label"]}' )
    hash_object = hashlib.sha1( str_in_hash.encode() )
    hash_main = hash_object.hexdigest()
    hash_yoomoney = webhook_answer['sha1_hash']
    logging.info(f'hash_main - {hash_main}' )
    logging.info(f'hash_yoomoney - {hash_yoomoney}' )
    return hash_main == hash_yoomoney

async def rate_limiter(request: web.Request):
    """Ограничение частоты запросов."""
    client_ip = request.remote
    if client_ip not in request_counter:
        request_counter[client_ip] = [0, asyncio.get_event_loop().time()]  # [счетчик, время первого запроса]
    counter, first_request_time = request_counter[client_ip]

    # Сбрасываем счетчик через минуту
    if asyncio.get_event_loop().time() - first_request_time > 60:
        request_counter[client_ip] = [1, asyncio.get_event_loop().time()]
        return True

    # Проверяем лимит
    if counter < RATE_LIMIT:
        request_counter[client_ip][0] += 1
        return True

    return False


async def webhook_handler(request: web.Request):
    """Основной обработчик вебхуков."""
    # Проверка частоты запросов
    if not await rate_limiter(request):
        logger.warning(f"Rate limit exceeded for IP: {request.remote}")
        return web.Response(status=429, text="Rate limit exceeded")

    # Проверка подлинности
    if not await validate_request(request):
        logger.warning(f"Invalid signature from IP: {request.remote}")
        return web.Response(status=403, text="Invalid signature")

    # Получение экземпляра бота из контекста приложения
    webhook_answer = await request.post()
    # Лог успешного запроса
    logger.info( f"Valid notification received: {webhook_answer}" )
    label = webhook_answer.get('label').split( '-' )

    price = label[2]
    withdraw_amount = webhook_answer.get('withdraw_amount')
    if float(withdraw_amount) == float(price):
        bot = request.app["bot"]
        user_id = label[0]
        id_rate = label[1]
        session = bot.data['session_maker']
        all_info_rate = await select_price_subscription_from_id(session=session, id_rate = id_rate)
        day_rate = all_info_rate[0]['number_of_days']
        await insert_paid_subscription(session=session, user_id=user_id, number_of_day=int(day_rate))
        try:
            text = 'Вы подписались на бота'
            await bot.send_message(chat_id=user_id, text=text)
            logger.info(f"Notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
    # Пример отправки сообщения пользователю
    # user_id = data.get("label")  # label используется как идентификатор пользователя
    # message = f"Вы получили оплату на сумму {data.get('amount')} {data.get('currency')}."
    # try:
    #     await bot.send_message(chat_id=user_id, text=message)
    #     logger.info(f"Notification sent to user {user_id}")
    # except Exception as e:
    #     logger.error(f"Failed to send message to user {user_id}: {e}")

    return web.Response(status=200, text="OK")

def create_app(bot):
    """Создание приложения AioHTTP с передачей экземпляра бота."""
    app = web.Application()
    app["bot"] = bot  # Передаем экземпляр бота в контекст приложения
    app.router.add_post("/webhook", webhook_handler)
    app.on_startup.append(on_startup)  # Добавляем действия при старте
    app.on_cleanup.append(on_cleanup)  # Добавляем действия при завершении
    return app
