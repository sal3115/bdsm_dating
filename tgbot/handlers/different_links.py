import logging

# from aiogram import types, Dispatcher
#
# from tgbot.models.sql_request import select_different_links
# from tgbot.services.auxiliary_functions import edit_message
#
#
# async def different_links_func(message:types.Message):
#     session = message.bot.data['session_maker']
#     all_info = await select_different_links(session=session)
#     if len(all_info) == 0:
#         text = 'В данном разделе пока ничего нет'
#         await edit_message(message=message, text=text)
#     elif len(all_info) > 0:
#         text = ''
#         for info in all_info:
#             text += f'{info["description"]} -\n' \
#                 f'{info["link"]}\n\n'
#         await edit_message(message=message, text=text)
#
#
# def description_link_handler(dp:Dispatcher):
#     dp.register_message_handler(different_links_func, text = '📱Разные ссылки', is_user = True)
#     dp.register_message_handler(different_links_func, text = '📱Разные ссылки', is_user_exit = True)
