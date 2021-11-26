from ssbbot.models import Profile, Stuff

import logging
import os
import re

import aiogram.utils.markdown as fmt
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from django.core.management.base import BaseCommand

import aiogram.utils.markdown as fmt
import time
from datetime import date, timedelta
from pytimeparse import parse
import pyqrcode
from geopy.distance import geodesic as GD

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


logging.basicConfig(level=logging.INFO)
load_dotenv()
token = os.getenv("BOT_KEY")
user_data = {}
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FsmAdmin(StatesGroup):
    first_name = State()
    last_name = State()
    email = State()
    passport = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('Отправить свою локацию 🗺️', request_location=True)
    )
    await message.answer("Привет! Я помогу вам арендовать личную ячейку для хранения вещей.\n"
     "Пришлите мне, пожалуйста, свою геолокацию, чтобы вы выбрали ближайший склад!", reply_markup=keyboard)

@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Location):
    user_data['lat'] = message.location.latitude
    user_data['lon'] = message.location.longitude
    user_location = (user_data['lat'], user_data['lon'])
    location_anino = (55.581818, 37.594978)
    location_chinatown = (55.75634, 37.63002)
    location_vdnh = (55.82177, 37.64107)
    location_mitino = (55.84589, 37.35909)
    location_spartak = (55.8176765, 37.4345436)
    location_sokol = (55.80518, 37.51495)
    distance_anino = round(GD(user_location, location_anino).km)
    distance_chinatown = round(GD(user_location, location_chinatown).km)
    distance_vdnh = round(GD(user_location, location_vdnh).km)
    distance_mitino = round(GD(user_location, location_mitino).km)
    distance_spartak = round(GD(user_location, location_spartak).km)
    distance_sokol = round(GD(user_location, location_sokol).km)


    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    buttons = [
        f"метро Анино \n({distance_anino} км от вас)",
        f"метро Китай-Город \n({distance_chinatown} км от вас)",
        f"метро ВДНХ \n({distance_vdnh} км от вас)",
        f"метро Митино \n({distance_mitino} км от вас)",
        f"метро Спартак \n({distance_spartak} км от вас)",
        f"метро Сокол \n({distance_sokol} км от вас)",
    ]
    keyboard.add(*buttons)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Какой адрес вам подходит?', reply_markup=keyboard)


@dp.message_handler(text_contains="метро")
async def sklad_1_answer(message: types.Message):
    user_data['adress'] = message.text

  
    keyboard = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)

    buttons = [
        types.InlineKeyboardButton(text='сезонные вещи', callback_data='сезонные вещи'),
        types.InlineKeyboardButton(text='другое', callback_data='другое')
    ]
    keyboard.add(*buttons)
    await bot.delete_message(message.from_user.id, message.message_id)
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
            text=f'{cell} шт', callback_data=f'{cell} шт') for cell in range(1, 11)
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=5, resize_keyboard=True)
    keyboard.add(*buttons)
    await call.message.answer("Укажите количество вещей для хранения.", reply_markup=keyboard)
    await call.answer()


@ dp.callback_query_handler(text_contains='шт')
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
    await call.message.answer("Выберите период хранения.", reply_markup=keyboard)
    await bot.delete_message(call.from_user.id, call.message.message_id)
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
            text="Забронировать", callback_data='Забронировать')
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
    keyboard = types.InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [
        types.InlineKeyboardButton(
            text=f'{cell} кв м', callback_data=f'{cell}w') for cell in range(1, 11)
    ]
    keyboard.add(*buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("Выберите размер ячейки:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text_contains='w')
async def send_date(call: types.CallbackQuery):
    user_data['size_cell'] = call.data
    buttons = [
        types.InlineKeyboardButton(
            text=f"{month} мес", callback_data=f"{month}a") for month in range(1, 13)
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    keyboard.add(*buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("Выберите срок аренды:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(text_contains='a')
async def choice_month(call: types.CallbackQuery):
    user_data['rent'] = call.data
    month = re.findall(r'\d+', call.data)
    size = re.findall(r'\d+', user_data['size_cell'])
    if size == "1":
        price_one_month = 599
    else:
        price_one_month = ((int(*size) - 1) * 150) + 599
    total_price = price_one_month * int(*month)

    keyboard_reg = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    key = types.KeyboardButton(text="Регистрация")
    keyboard_reg.add(key)

    period_days = int(*month)*30.5
    user_data['period_days'] = period_days
    user_data['total_price'] = total_price
    user_data['quantity'] = size[0]
    user_data['item'] = 'другое'

    buttons = [
        types.InlineKeyboardButton(
            text="Забронировать", callback_data='Забронировать')
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Вы выбрали:")),
            fmt.text(f"\nРазмер ячейки:   {int(*size)} кв м"),
            fmt.text(f"\nСрок аренды:   {int(*month)} месяцев"),
            fmt.text(f"\nПо адресу:   {user_data['adress']}"),
            fmt.text(f"\nСтоимость итого:   {total_price} рублей"), sep="\n",
        ), reply_markup=keyboard,
    )
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


@ dp.callback_query_handler(text='Забронировать')
async def registration(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    user = call.message["chat"]["first_name"]
    
    try:
        Profile.objects.get(external_id=call.from_user.id)
        buttons = [
        types.InlineKeyboardButton(
            text="Оплатить", callback_data='Оплатить')
        ]
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)
        await call.message.answer(f' {user}, вы уже у нас зарегистрированы, рады видеть вас снова! '
                ' Для оплаты нажмите кнопку ниже:', reply_markup=keyboard)
        await call.answer()
    except:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        buttons = [
            "Регистрация",
            "Отмена",
        ]
        keyboard.add(*buttons)
        await call.message.answer(f' {user}, вы у нас впервые? Давайте зарегистрируемся.', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Отмена")
async def cancel(message: types.Message):
    await message.answer('Мне жаль, что вы уходите, но если передумаете - нажмите /start')


@dp.message_handler(text="Регистрация")
async def registration(message: types.Message):
    user_id = message.from_user.id
    doc = open('pd.pdf', 'rb')
    await bot.send_document(user_id, doc)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [
            "Принять",
            "Отказаться",
    ]
    keyboard.add(*buttons)
    await bot.send_message(
        user_id,
        "Для заказа нужно ваше согласие на обработку персональных данных.",
        reply_markup=keyboard,
        )

@dp.message_handler(state=None)
async def begin(message: types.Message):
    if message.text == 'Принять':
        await FsmAdmin.first_name.set()
        await bot.send_message(message.from_user.id, 'Укажите имя')
    if message.text == 'Отказаться':
        user_id = message.from_user.id
        doc = open('pd.pdf', 'rb')
        await bot.send_document(user_id, doc)
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        buttons = [
            "Принять",
            "Отказаться",
        ]
        keyboard.add(*buttons)
        await bot.send_message(
        user_id,
        "Извините, без согласия на обработку данных заказы невозможны.",
        reply_markup=keyboard,
        )


@dp.message_handler(state=FsmAdmin.first_name, regexp='[А-Яа-я]')
async def first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["first_name"] = message.text
    await bot.send_message(message.from_user.id, 'Укажите фамилию')
    await FsmAdmin.next()


@dp.message_handler(state=FsmAdmin.last_name, regexp='[А-Яа-я]')
async def last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["last_name"] = message.text
    await bot.send_message(message.from_user.id, 'Укажите паспортные данные')
    await FsmAdmin.next()


#@dp.message_handler(state=FsmAdmin.email, regexp='[\w\.-]+@[\w\.-]+(\.[\w]+)+')
@dp.message_handler(state=FsmAdmin.email, regexp='[А-Яа-я]')
async def passport(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["passport"] = message.text
    await message.answer('Укажите дату рождения')
    await FsmAdmin.next()


@dp.message_handler(state=FsmAdmin.passport, regexp='[\d+]')
async def first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["birthday"] = message.text
    #await FsmAdmin.next()
    await bot.delete_message(message.from_user.id, message.message_id)
    buttons = [
    types.InlineKeyboardButton(
        text="Оплатить", callback_data='Оплатить')
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    # profile = Profile.objects.create(
    #     external_id=message.from_user.id,
    #     username = message["chat"]["username"] or '',
    #     first_name = data["first_name"],
    #     last_name = data["last_name"],
    #     #contact = data["contact"],
    #     passport = data["passport"],
    #     birthday = data["birthday"],
    #     )
    # profile.save()
    await message.answer(f' {data["first_name"]}, вы зарегистрированы! '
            ' Для оплаты нажмите кнопку ниже:', reply_markup=keyboard)
    await FsmAdmin.next()



@ dp.callback_query_handler(text='Оплатить')
async def send_qrcode(call: types.CallbackQuery):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f'{call.message.chat.id}_{timestr}.png'
    images_dir = os.path.join(os.getcwd(), 'QR')
    os.makedirs(images_dir, exist_ok=True)
    filepath = os.path.join(images_dir, filename)
    code = f'{timestr}_{call.message.chat.id}_'
    url=pyqrcode.create(code)
    url.png(filepath,scale=15)
    profile=Profile.objects.get(external_id=call.from_user.id)
    today = date.today()
    storage_date_end = today + timedelta(days=user_data['period_days'])
    storage_date_end = storage_date_end.strftime("%d.%m.%Y")
    storage_date_start = today.strftime("%d.%m.%Y")
    quantity = user_data['quantity']
    quantity = re.findall(r'\d+', quantity)[0]
    stuff = Stuff.objects.create(
    profile=profile,
    storage=user_data['adress'],
    description=user_data['item'],
    quantity=quantity,
    period=f'{storage_date_start}-{storage_date_end}',
    price=user_data['total_price'],
    code=filename,
    )
    stuff.save()

    await call.message.answer('Заказ создан и успешно оплачен!'
            ' Вот ваш электронный ключ для доступа к вашему личному складу. '
            f'Вы сможете попасть на склад в любое время в период с {storage_date_start} по {storage_date_end}')
    photo = open(filepath, 'rb')
    await bot.send_photo(chat_id=call.message.chat.id, photo=photo)
    await call.message.answer('Спасибо за заказ! Если хотите сделать еще один - нажмите /start')
    

 

#if __name__ == '__main__':
#   executor.start_polling(dp, skip_updates=True)


class Command(BaseCommand):
     executor.start_polling(dp, skip_updates=True)
