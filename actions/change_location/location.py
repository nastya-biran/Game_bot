from main import cur, Game, in_city_keyboard, in_dungeon_keyboard, dp, scheduler
from aiogram import  types
from aiogram.dispatcher.filters import Text
from sqlalchemy import select
from math import sqrt, ceil
import db
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from datetime import datetime, timedelta



@dp.message_handler(Text(["Переместиться в другой город"]), state = Game.in_city)
async def select_city(message: types.Message):
    user_id = message.from_user.id
    cities_buttons = await get_available_locations_keyboard(user_id, "city")
    cities_buttons.append([types.KeyboardButton(text="Остаться в нынешнем городе")])
    cities_keyboard = types.ReplyKeyboardMarkup(keyboard=cities_buttons, resize_keyboard=True)
    await Game.select_city.set()
    await message.answer("Выбери город!", reply_markup=cities_keyboard)

async def get_available_locations_keyboard(user_id, category):
    locations = cur.session.execute(select(db.Locations).where(db.Locations.loc_type == category)).scalars().all()
    available_locations = []
    for location in locations:
        is_reachable, time = await check_locations(user_id, location)
        if is_reachable:
            available_locations.append(location.name)
    location_buttons = []
    for location_name in available_locations:
        location_buttons.append([types.KeyboardButton(text=location_name)])
    return location_buttons


@dp.message_handler(state = Game.select_city)
async def change_city(message: types.Message):
    await Game.in_city.set()
    user_id = message.from_user.id
    city_name = message.text
    if message.text == "Остаться в нынешнем городе":
        await message.answer(f"Ну и правильно, не надо никуда ехать!", reply_markup=in_city_keyboard)
        return
    selected_city = cur.session.execute(select(db.Locations).where(db.Locations.name == city_name)).scalar()
    if selected_city is not None:
        is_reachable, time = await check_locations(user_id, selected_city)
        if is_reachable:
            await message.answer(f"Вы отправляетесь в город {selected_city.name}. Время поездки в секундах: {time}", reply_markup=ReplyKeyboardRemove())
            if time != 0:
                await Game.blocking_state.set()
                moment = datetime.now() + timedelta(seconds=time)
                scheduler.add_job(free_state, "date", run_date=moment, args=[user_id, selected_city, message, True, in_city_keyboard])
            else:
                await free_state(user_id, selected_city, message, True, in_city_keyboard)
        else:
            await message.answer(f"Этот город слишком далеко!", reply_markup=in_city_keyboard)
    else:
        await message.answer(f"Такого города нет!", reply_markup=in_city_keyboard)

async def free_state(user_id, location, message, city, reply_markup):
    location_name = "город"
    if not city:
        location_name = "подземелье"
        await Game.in_dungeon.set()
    else:
        await Game.in_city.set()
    await message.answer(f"Вы переместились в {location_name}: {message.text}", reply_markup=reply_markup)
    cur.session.query(db.Person).where(db.Person.user_id == user_id).update({'location_id': location.location_id,
                                                                             'hp': 100})
    cur.session.commit()

@dp.message_handler(state = Game.blocking_state)
async def block_message(message: types.Message):
    await message.answer(f"Вы направляетесь в другую локацию, на данный момент все ваши действия заблокированы.")

@dp.message_handler(Text(["Пойти в подземелье"]), state = Game.in_city)
async def select_dungeon(message: types.Message):
    user_id = message.from_user.id
    dungeon_buttons = await get_available_locations_keyboard(user_id, "dungeon")
    dungeon_buttons.append([types.KeyboardButton(text="Вернуться в город(я слабый)")])
    dungeon_keyboard = types.ReplyKeyboardMarkup(keyboard=dungeon_buttons, resize_keyboard=True)
    await Game.select_dungeon.set()
    await message.answer("Выбери подземелье!", reply_markup=dungeon_keyboard)

@dp.message_handler(state = Game.select_dungeon)
async def to_dungeon(message: types.Message):
    user_id = message.from_user.id
    dungeon_name = message.text
    if message.text == "Вернуться в город(я слабый)":
        await message.answer(f"Ну вы и даете конечно", reply_markup=in_city_keyboard)
        await Game.in_city.set()
        return
    selected_dungeon = cur.session.execute(select(db.Locations).where(db.Locations.name == dungeon_name)).scalar()
    if selected_dungeon is not None:
        is_reachable, time = await check_locations(user_id, selected_dungeon)
        if is_reachable:
            await message.answer(f"Вы отправляетесь в подеземелье {selected_dungeon.name}. Время поездки в секундах: {time}",
                                 reply_markup=ReplyKeyboardRemove())
            if time != 0:
                await Game.blocking_state.set()
                moment = datetime.now() + timedelta(seconds=time)
                scheduler.add_job(free_state, "date", run_date=moment, args=[user_id, selected_dungeon, message, False, in_dungeon_keyboard])
            else:
                await free_state(user_id, selected_dungeon, message, False, in_dungeon_keyboard)
        else:
            await message.answer(f"Это подземелье слишком далеко!", reply_markup=in_city_keyboard)
            await Game.in_city.set()
    else:
        await message.answer(f"Такого подземелья нет!", reply_markup=in_city_keyboard)
        await Game.in_city.set()



async def check_locations(user_id, location):
    cur_loc_id = cur.session.query(db.Person).get(user_id).location_id
    cur_loc_x = cur.session.query(db.Locations).get(cur_loc_id).x_coord
    cur_loc_y = cur.session.query(db.Locations).get(cur_loc_id).y_coord
    dist = sqrt((location.x_coord - cur_loc_x) ** 2 + (location.y_coord - cur_loc_y) ** 2)
    if dist <= 10 and cur_loc_id != location.location_id:
        return True, ceil(dist)
    else:
        return False, -1




