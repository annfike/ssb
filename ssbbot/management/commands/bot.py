from ssbbot.models import Profile, Stuff

import logging
import os
import re

import aiogram.utils.markdown as fmt
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from django.core.management.base import BaseCommand

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
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [
        "метро Анино",
        "метро Китай-Город",
        "метро ВДНХ",
        "метро Митино",
        "метро Спартак",
        "метро Сокол",
    ]
    keyboard.add(*buttons)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Выберите адрес склада:', reply_markup=keyboard)


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
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer('yyy', reply_markup=types.ReplyKeyboardRemove())
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
    await call.message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Вы выбрали:")),
            fmt.text(f"\nРазмер ячейки:   {int(*size)} кв м"),
            fmt.text(f"\nСрок аренды:   {int(*month)} месяцев"),
            fmt.text(f"\nПо адресу:   {user_data['adress']}"),
            fmt.text(f"\nСтоимость итого:   {total_price} рублей"), sep="\n",
        ), reply_markup=keyboard,
    )
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, "Для продолжения пройдите регистрацию")
    await call.answer()


@dp.message_handler(text="Регистрация")
async def registration(message: types.Message):
    keyboard_ok = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    key = types.KeyboardButton(text='Согласен')
    keyboard_ok.add(key)
    await bot.send_message(
        message.from_user.id,
        "Ознакомьтесь с согласием на обработку персональных данных. ФАЙЛ",
        reply_markup=keyboard_ok,
    )


@dp.message_handler(state=None)
async def begin(message: types.Message):
    if message.text == 'Согласен':
        await FsmAdmin.first_name.set()
        await bot.send_message(message.from_user.id, 'Укажите имя')


@dp.message_handler(state=FsmAdmin.first_name, regexp='[А-Яа-я]')
async def first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["first_name"] = message.text
    await FsmAdmin.next()

    await bot.send_message(message.from_user.id, 'Укажите фамилию')


@dp.message_handler(state=FsmAdmin.last_name, regexp='[А-Яа-я]')
async def first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["last_name"] = message.text
    await FsmAdmin.next()
    await bot.send_message(message.from_user.id, 'Укажите email')


@dp.message_handler(state=FsmAdmin.email, regexp='[\w\.-]+@[\w\.-]+(\.[\w]+)+')
async def first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["email"] = message.text
    await FsmAdmin.next()
    await message.answer('Укажите passport')


@dp.message_handler(state=FsmAdmin.pasport, regexp='[\d+]')
async def first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["passport"] = message.text
    await FsmAdmin.next()
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.send_message(message.from_user.id, '...!!')


# if __name__ == '__main__':
#    executor.start_polling(dp, skip_updates=True)


class Command(BaseCommand):
    executor.start_polling(dp, skip_updates=True)
