from django.core.management.base import BaseCommand
from ssbbot.models import Profile, Stuff

import logging
import os
import re

from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import aiogram.utils.markdown as fmt

logging.basicConfig(level=logging.INFO)
load_dotenv()
token = os.getenv("BOT_KEY")
user_data = {}
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        "метро Анино",
        "метро Китай-Город",
        "метро ВДНХ",
        "метро Митино",
        "метро Спартак",
        "метро Сокол",
    ]
    keyboard.add(*buttons)
    await message.answer('Выберите адрес склада:', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "метро Анино")
@dp.message_handler(lambda message: message.text == "метро Китай-Город")
@dp.message_handler(lambda message: message.text == "метро ВДНХ")
@dp.message_handler(lambda message: message.text == "метро Митино")
@dp.message_handler(lambda message: message.text == "метро Спартак")
@dp.message_handler(lambda message: message.text == "метро Сокол")
async def sklad_1_answer(message: types.Message):

    #print(message["chat"]) #{"id": 110968809, "first_name": "Anna", "username": "annfike", "type": "private"}
    #print(message["chat"]["first_name"]) #Anna

    user_data['adress'] = message.text
    await message.answer("Ок!", reply_markup=types.ReplyKeyboardRemove())
    

    buttons = [
        types.InlineKeyboardButton(text='сезонные вещи', callback_data='сезонные вещи'),
        types.InlineKeyboardButton(text='другое', callback_data='другое')
               ]
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)

    await message.answer("Что хотите хранить?:", reply_markup=keyboard)


@dp.callback_query_handler(text='сезонные вещи')
async def send_msg(call: types.CallbackQuery):
    buttons = [
        types.InlineKeyboardButton(text='Лыжи', callback_data='Лыжи'),
        types.InlineKeyboardButton(text='Сноуборд', callback_data='Сноуборд'),
        types.InlineKeyboardButton(text='Велосипед', callback_data='Велосипед'),
        types.InlineKeyboardButton(text='Колеса', callback_data='Колеса'),
               ]

    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Выберите из списка:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text='Лыжи')
@dp.callback_query_handler(text='Сноуборд')
@dp.callback_query_handler(text='Велосипед')
@dp.callback_query_handler(text='Колеса')
async def seasonal_choose_quantity(call: types.CallbackQuery):
    user_data['item'] = call.data
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Условия:\n\n")),
            fmt.text('1 лыжи - 100 р/неделя или 300 р/мес\n'),
            fmt.text('1 сноуборд - 100 р/неделя или 300 р/мес\n'),
            fmt.text('4 колеса - 200 р/мес\n'),
            fmt.text('1 велосипед - 150 р/ неделя или 400 р/мес\n'),
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cell} шт', callback_data=f'{cell} шт') for cell in range(1,11)
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=5, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Укажите количество вещей для хранения.", reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text='1 шт')
@ dp.callback_query_handler(text='2 шт')
@ dp.callback_query_handler(text='3 шт')
@ dp.callback_query_handler(text='4 шт')
@ dp.callback_query_handler(text='5 шт')
@ dp.callback_query_handler(text='6 шт')
@ dp.callback_query_handler(text='7 шт')
@ dp.callback_query_handler(text='8 шт')
@ dp.callback_query_handler(text='9 шт')
@ dp.callback_query_handler(text='10 шт')
async def seasonal_choose_period(call: types.CallbackQuery):
    user_data['quantity'] = call.data
    buttons = [
        types.InlineKeyboardButton(text='1 неделя', callback_data='1 неделя'),
        types.InlineKeyboardButton(text='2 недели', callback_data='2 недели'),
        types.InlineKeyboardButton(text='3 недели', callback_data='3 недели'),
        types.InlineKeyboardButton(text='1 месяц', callback_data='1 месяц'),
        types.InlineKeyboardButton(text='2 месяца', callback_data='2 месяца'),
        types.InlineKeyboardButton(text='3 месяца', callback_data='3 месяца'),
        types.InlineKeyboardButton(text='4 месяца', callback_data='4 месяца'),
        types.InlineKeyboardButton(text='5 месяцев', callback_data='5 месяцев'),
        types.InlineKeyboardButton(text='6 месяцев', callback_data='6 месяцев'),
               ]

    keyboard = types.InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Принято! Выберите период хранения.", reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text='1 неделя')
@ dp.callback_query_handler(text='2 недели')
@ dp.callback_query_handler(text='3 недели')
@ dp.callback_query_handler(text='1 месяц')
@ dp.callback_query_handler(text='2 месяца')
@ dp.callback_query_handler(text='3 месяца')
@ dp.callback_query_handler(text='4 месяца')
@ dp.callback_query_handler(text='5 месяцев')
@ dp.callback_query_handler(text='6 месяцев')
async def seasonal_book(call: types.CallbackQuery):
    user_data['rent'] = call.data
    periods = {
            '1 неделя': 7,
            '2 недели': 14,
            '3 недели': 21,
            '1 месяц': 31,
            '2 месяца': 61,
            '3 месяца': 92,
            '4 месяца': 122,
            '5 месяцев': 153,
            '6 месяцев': 184,
            }
    prices = {
    'Лыжи': {
        '1 неделя': 100,
        '2 недели': 200,
        '3 недели': 300,
        '1 месяц': 300,
        '2 месяца': 600,
        '3 месяца': 900,
        '4 месяца': 1200,
        '5 месяцев': 1500,
        '6 месяцев': 1800,
        },
    'Велосипед': {
        '1 неделя': 150,
        '2 недели': 300,
        '3 недели': 450,
        '1 месяц': 400,
        '2 месяца': 800,
        '3 месяца': 1200,
        '4 месяца': 1600,
        '5 месяцев': 2000,
        '6 месяцев': 2400,
        },
    'Сноуборд': {
        '1 неделя': 100,
        '2 недели': 200,
        '3 недели': 300,
        '1 месяц': 300,
        '2 месяца': 600,
        '3 месяца': 900,
        '4 месяца': 1200,
        '5 месяцев': 1500,
        '6 месяцев': 1800,
        },
    'Колеса': {
        '1 месяц': 200,
        '2 месяца': 400,
        '3 месяца': 600,
        '4 месяца': 800,
        '5 месяцев': 1000,
        '6 месяцев': 1200,
        },
    }
    period = user_data['rent']
    period_days = periods[period]
    storage = user_data['adress']
    item = user_data['item']
    quantity = user_data['quantity']
    quantity = re.findall(r'\d+', quantity)[0]
   
    total_price = int(quantity) * prices[item][period]
    user_data['period_days'] = period_days
    user_data['total_price'] = total_price

    buttons = [
        types.InlineKeyboardButton(
            text="Забронировать", callback_data='ok')
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Вы выбрали:")),
            fmt.text(f"\nЧто храним:   {item} "),
            fmt.text(f"\nСрок аренды:   {period} "),
            fmt.text(f"\nПо адресу:   {storage}"),
            fmt.text(f"\nСтоимость:   {total_price} рублей"), sep="\n"
        ), reply_markup=keyboard)

    print(user_data)
    await call.answer()









@dp.callback_query_handler(text='другое')
async def send_msg_other(call: types.CallbackQuery):
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Условия:\n\n")),
            fmt.text("599 руб - первый 1 кв.м., далее +150 руб за каждый кв. метр в месяц")
        ),
        reply_markup=types.ReplyKeyboardRemove()
    )
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cell} кв м', callback_data=f'{cell}') for cell in range(1, 11)
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Выберите размер ячейки:", reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text='1')
@ dp.callback_query_handler(text='2')
@ dp.callback_query_handler(text='3')
@ dp.callback_query_handler(text='4')
@ dp.callback_query_handler(text='5')
@ dp.callback_query_handler(text='6')
@ dp.callback_query_handler(text='7')
@ dp.callback_query_handler(text='8')
@ dp.callback_query_handler(text='9')
@ dp.callback_query_handler(text='10')
async def send_date(call: types.CallbackQuery):
    user_data['size_cell'] = call.data
    buttons = [
        types.InlineKeyboardButton(
            text=f"{month} мес", callback_data=f"{month}a") for month in range(1, 13)
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Выберите срок аренды:", reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text='1a')
@ dp.callback_query_handler(text='2a')
@ dp.callback_query_handler(text='3a')
@ dp.callback_query_handler(text='4a')
@ dp.callback_query_handler(text='5a')
@ dp.callback_query_handler(text='6a')
@ dp.callback_query_handler(text='7a')
@ dp.callback_query_handler(text='8a')
@ dp.callback_query_handler(text='9a')
@ dp.callback_query_handler(text='10a')
@ dp.callback_query_handler(text='11a')
@ dp.callback_query_handler(text='12a')
async def choice_month(call: types.CallbackQuery):
    user_data['rent'] = call.data
    month = re.findall(r'\d+', call.data)
    if user_data['size_cell'] == "1":
        price_one_month = 599
    else:
        price_one_month = ((int(user_data['size_cell']) - 1) * 150) + 599
    total_price = price_one_month * int(*month)
    buttons = [
        types.InlineKeyboardButton(
            text="Забронироавать", callback_data='ok')
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Вы выбрали:")),
            fmt.text(f"\nРазмер ячейки:   {user_data['size_cell']} кв м"),
            fmt.text(f"\nСрок аренды:   {int(*month)} месяцев"),
            fmt.text(f"\nПо адресу:   {user_data['adress']}"),
            fmt.text(f"\nСтоимость итого:   {total_price} рублей"), sep="\n"
        ), reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text='ok')
async def registration(call: types.CallbackQuery):
    await call.message.answer('хз', reply_markup=types.ReplyKeyboardRemove())
    await call.answer()


#if __name__ == '__main__':
#    executor.start_polling(dp, skip_updates=True)

class Command(BaseCommand):
    executor.start_polling(dp, skip_updates=True)