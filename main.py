import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, CommandStart
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import db, initialise_db
from sqlalchemy import select
from math import sqrt
from random import randint
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.start()


TOKEN = "5850505052:AAEbjZiAW0EzxgStq103WwOILzUhqsl520o"
class Game(StatesGroup):
    select_nickname = State()
    in_city = State()
    select_city = State()
    select_dungeon = State()
    in_dungeon = State()
    in_shop = State()
    in_shop_armour = State()
    in_shop_weapon = State()
    in_shop_potion = State()
    select_item_to_sale = State()
    select_num_items_to_sale = State()
    in_inventory = State()
    select_active_inventory = State()
    person_move = State()
    mob_move = State()
    blocking_state = State()


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
cur = db.MySession()


in_city_buttons = [[types.KeyboardButton(text="Пойти в магазин")],
                   [types.KeyboardButton(text="Информация о себе")],
                   [types.KeyboardButton(text="Посмотреть свой инвентарь и поменять активный инвентарь")],
                   [types.KeyboardButton(text="Переместиться в другой город")],
                   [types.KeyboardButton(text="Пойти в подземелье")]]

in_city_keyboard = types.ReplyKeyboardMarkup(keyboard=in_city_buttons, resize_keyboard=True)

section_buttons = [[types.KeyboardButton(text="Оружие")],
                   [types.KeyboardButton(text="Броня и амуниция")],
                   [types.KeyboardButton(text="Зелья")],
                   [types.KeyboardButton(text="Продать свой инвентарь")],
                   [types.KeyboardButton(text="Выйти из магазина")]]
section_keyboard = types.ReplyKeyboardMarkup(keyboard=section_buttons, resize_keyboard=True)

inventory_buttons = [[types.KeyboardButton(text="Посмотреть активный инвентарь")],
                     [types.KeyboardButton(text="Изменить активный инвентарь")],
                     [types.KeyboardButton(text="Выйти из инвентаря")]]
inventory_keyboard = types.ReplyKeyboardMarkup(keyboard=inventory_buttons, resize_keyboard=True)

dungeon_buttons = [[types.KeyboardButton(text="Начать бой!")]]
in_dungeon_keyboard = types.ReplyKeyboardMarkup(keyboard=dungeon_buttons, resize_keyboard=True)

fight_buttons = [[types.KeyboardButton(text="Обычная атака")],
                 [types.KeyboardButton(text="Магическая атака")]]
fight_keyboard = types.ReplyKeyboardMarkup(keyboard=fight_buttons, resize_keyboard=True)

available_items_in_shop =[]

available_items_to_sale = []

item_to_sale_id : int

available_inventory = []

selected_mob: db.Mobs

@dp.message_handler(CommandStart(), state = '*')
async def start_bot(message: types.Message):
    await Game.select_nickname.set()
    await message.answer("Привет, я бот с которым ты можешь погрузиться в увлекательное приключение с монстрами и битвами! Введи имя персонажа, чтобы мы могли начать!")




@dp.message_handler(state = Game.select_nickname)
async def start_game(message: types.Message):
    nickname = message.text
    user_id = message.from_user.id
    db.create_person(cur.session, nickname, user_id)
    await Game.in_city.set()
    await message.answer(text=f"Добро пожаловать, {nickname}!")
    await message.answer("Вы переместились в город: Цитадель", reply_markup=in_city_keyboard)

@dp.message_handler(Text(["Информация о себе"]), state = Game.in_city)
async def get_details(message: types.Message):
    user_id = message.from_user.id
    details = str(cur.session.query(db.Person).get(user_id))
    await message.answer(text=details, reply_markup=in_city_keyboard)


if __name__ == '__main__':
    initialise_db.init_db(cur.session)
    from actions import dp
    executor.start_polling(dp, skip_updates=True)

