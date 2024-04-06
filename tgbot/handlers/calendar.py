import datetime

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from loader import dp
from Keyboards.kb_calendar import func_kb_calendar

# ловим прошлый год
@dp.callback_query_handler(Text(startswith='backyear'), state='*')
async def backtear(callback: types.CallbackQuery):
    _datestr = callback.data.split('_')[2].split('-')
    print(33)
    _date = datetime.date(int(_datestr[2]) - 1, int(_datestr[1]), int(_datestr[0]))
    cb = callback.data.split('_')[1]
    kb = await func_kb_calendar(cb, _date)
    await callback.message.edit_text(text='Выбирай', reply_markup=kb)
    await callback.answer()

# ловим следующий год
@dp.callback_query_handler(Text(startswith='nextyear'), state='*')
async def backtear(callback: types.CallbackQuery):
    _datestr = callback.data.split('_')[2].split('-')
    print(33)
    _date = datetime.date(int(_datestr[2]) + 1, int(_datestr[1]), int(_datestr[0]))
    cb = callback.data.split('_')[1]
    kb = await func_kb_calendar(cb, _date)
    await callback.message.edit_text(text='Выбирай', reply_markup=kb)
    await callback.answer()


# ловим прошлый месяц
@dp.callback_query_handler(Text(startswith='backmonth'), state='*')
async def backtear(callback: types.CallbackQuery):
    _datestr = callback.data.split('_')[2].split('-')
    print(33)
    _date = datetime.date(int(_datestr[2]), int(_datestr[1]), int(_datestr[0]))
    _date = _date - datetime.timedelta(days=1)
    cb = callback.data.split('_')[1]
    kb = await func_kb_calendar(cb, _date)
    await callback.message.edit_text(text='Выбирай', reply_markup=kb)
    await callback.answer()


# ловим следующий месяц
@dp.callback_query_handler(Text(startswith='nextmonth'), state='*')
async def backtear(callback: types.CallbackQuery):
    _datestr = callback.data.split('_')[2].split('-')
    print(33)
    _date = datetime.date(int(_datestr[2]), int(_datestr[1]), int(_datestr[0]))
    _date = _date + datetime.timedelta(days=32)
    cb = callback.data.split('_')[1]
    kb = await func_kb_calendar(cb, _date)
    await callback.message.edit_text(text='Выбирай', reply_markup=kb)
    await callback.answer()