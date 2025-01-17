import asyncio
import hashlib
import logging

from quart import Quart, request, jsonify
from aiogram import Bot

from tgbot.config import load_config


# def create_app(bot: Bot):
#     app = Quart(__name__)
#     @app.route('/webhook', methods=['POST'])
#     async def webhook_handler():
#         webhook_answer = await request.form
#         webhook_answer = webhook_answer.to_dict()
#         logging.info(webhook_answer)
#         # config = load_config( ".env" )
#         # secret_str = config.yoomoney.secret_word_yoomoney
#         # str_in_hash = str(
#         #     f'{webhook_answer["notification_type"]}&{webhook_answer["operation_id"]}&{webhook_answer["amount"]}&'
#         #     f'{webhook_answer["currency"]}&{webhook_answer["datetime"]}&{webhook_answer["sender"]}&'
#         #     f'{webhook_answer["codepro"]}&{secret_str}&{webhook_answer["label"]}' )
#         # hash_object = hashlib.sha1( str_in_hash.encode() )
#         # hash_main = hash_object.hexdigest()
#         # hash_yoomoney = webhook_answer['sha1_hash']
#         # unaccepted = webhook_answer['unaccepted']
#         # if hash_main == hash_yoomoney:
#         #     if not unaccepted:
#         #         label = webhook_answer['label'].split( '-' )
#         #         user_id = label[0]
#         #         title = label[1]
#         #         price = label[2]
#         #         logging.info(user_id)
#         # else:
#         #     return '500'
#     return app
def create_quart_app(bot):
    """Создаем приложение Quart."""
    app = Quart(__name__)
    app.bot = bot

    @app.route("/")
    async def index():
        logging.info("Quart запущен и обработал запрос")
        return "Bot is running!"

    return app
# def create_quart_app(bot):
#     app = Quart(__name__)
#     @app.route( '/webhook', methods=['POST'] )
#     async def webhook_handler():
#         webhook_answer = await request.form
#         webhook_answer = webhook_answer.to_dict()
#         logging.info(webhook_answer)
#         # config = load_config( ".env" )
#         # secret_str = config.yoomoney.secret_word_yoomoney
#         # str_in_hash = str(
#         #     f'{webhook_answer["notification_type"]}&{webhook_answer["operation_id"]}&{webhook_answer["amount"]}&'
#         #     f'{webhook_answer["currency"]}&{webhook_answer["datetime"]}&{webhook_answer["sender"]}&'
#         #     f'{webhook_answer["codepro"]}&{secret_str}&{webhook_answer["label"]}' )
#         # hash_object = hashlib.sha1( str_in_hash.encode() )
#         # hash_main = hash_object.hexdigest()
#         # hash_yoomoney = webhook_answer['sha1_hash']
#         # unaccepted = webhook_answer['unaccepted']
#         # if hash_main == hash_yoomoney:
#         #     if not unaccepted:
#         #         label = webhook_answer['label'].split( '-' )
#         #         user_id = label[0]
#         #         title = label[1]
#         #         price = label[2]
#         #         logging.info(user_id)
#         # else:
#         #     return '500'
#
#     @app.route('/health', methods=['GET'])
#     async def health_check():
#         return jsonify({'status': 'running'}), 200
#     return app





# async def start_quart(bot: Bot, shutdown_event):
#     """Запуск веб-сервера Quart."""
#     app = create_app(bot)
#     async def shutdown():
#         # Ожидаем, пока не получим сигнал для завершения
#         await shutdown_event.wait()  # Ожидаем, пока shutdown_event не будет установлен
#         await app.shutdown()  # Завершаем приложение Quart
#
#     # Запуск в фоне функции shutdown, чтобы она могла завершить сервер
#     asyncio.create_task( shutdown() )  # Запускаем задачу завершения в фоне
#     # Запуск сервера Quart
#     await app.run_task(host="localhost", port=5602)
# async def start_quart(bot: Bot, shutdown_event):
#     """Запуск веб-сервера Quart."""
#     app = create_app(bot)
#     task = await app.run_task(host="localhost", port=5602)
#     await shutdown_event.wait()
#     task.cancel()  # Останавливаем сервер
#
#     try:
#         task
#     except asyncio.CancelledError:
#         pass