from main import cur, Game, in_city_keyboard, fight_keyboard, in_dungeon_keyboard, dp, scheduler
from aiogram import  types
from aiogram.dispatcher.filters import Text
from sqlalchemy import select
from math import sqrt
import db
from random import randint
from actions.change_location.location import get_available_locations_keyboard
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from copy import deepcopy
from datetime import datetime, timedelta

job = None

@dp.message_handler(Text(["Начать бой!"]), state = Game.in_dungeon)
async def start_fight(message: types.Message):
    await message.answer("Ну что же, желаю удачи!")
    user_id = message.from_user.id
    user_level = cur.session.execute(select(db.Person.level).where(db.Person.user_id == user_id)).scalar_one()
    available_mobs = cur.session.execute(select(db.Mobs).where(db.Mobs.req_level <= user_level)).scalars().all()
    global selected_mob

    selected_mob = deepcopy(available_mobs[randint(0, len(available_mobs) - 1)])
    await Game.person_move.set()
    await message.answer(f"На вас напал монстр! \n {str(selected_mob)}")
    global job
    job = scheduler.add_job(lose_in_one_minute, "date", run_date=datetime.now() + timedelta(seconds=60), args=[user_id, message])
    await message.answer("Ваш ход! У вас одна минута на ответ!", reply_markup=fight_keyboard)

async def lose_in_one_minute(user_id, message):
    nickname = cur.session.execute(select(db.Person.nickname).where(db.Person.user_id == user_id)).scalar_one()
    db.create_person(cur.session, nickname, user_id)
    await message.answer(
        f"Вы слишком долго думали, и монстр вас убил( Грустно, но иногда лучше думать поменьше")
    await Game.in_city.set()
    await message.answer(text=f"Добро пожаловать, {nickname}!")
    await message.answer("Вы переместились в город: Цитадель", reply_markup=in_city_keyboard)


@dp.message_handler(Text(["Магическая атака", "Обычная атака"]), state = Game.person_move)
async def person_attack(message: types.Message):
    job.remove()
    global selected_mob
    user_id = message.from_user.id
    cur_user = cur.session.execute(select(db.Person).where(db.Person.user_id == user_id)).scalar_one()
    damage_to_mob = max(0, cur_user.attack - selected_mob.armour)
    if message.text == "Магическая атака":
        damage_to_mob = max(0, cur_user.magic_attack - selected_mob.magic_armour)
    selected_mob.hp = max(0, selected_mob.hp - damage_to_mob)
    await message.answer(f"Ваш удар:  {message.text}\n"
                         f"Ваш урон монстру: {damage_to_mob}\n"
                         f"HP монстра: {selected_mob.hp}\n")
    if selected_mob.hp <= 0:
        await message.answer(f"Вы победили монстра, мои поздравления!")
        initial_mob = cur.session.query(db.Mobs).get(selected_mob.mob_id)
        cur.session.query(db.Person).where(db.Person.user_id == user_id).update({"money": db.Person.money + initial_mob.hp,
                                                                                          "xp": db.Person.xp + initial_mob.xp})
        cur.session.commit()
        await message.answer(f"Ваша награда: \n"
                             f"Монеты: {initial_mob.hp}\n"
                             f"XP: {initial_mob.xp}\n")
        if cur_user.xp + initial_mob.xp >= (cur_user.xp//100 + 1)*100:
            cur.session.execute(
                select(db.Person).where(db.Person.user_id == user_id).update({"level": db.Person.level + 1}))
            cur.session.commit()
            await message.answer(f"Как же вы круты! Вы повысили уровен до {cur_user.xp//100 + 1}")
        win_city_buttons = await get_available_locations_keyboard(user_id, "city")
        win_keyboard = types.ReplyKeyboardMarkup(keyboard=win_city_buttons, resize_keyboard=True)
        await message.answer("Выберите город, в котором восстановите силы!", reply_markup=win_keyboard)
        await Game.select_city.set()
    else:
        await message.answer("Теперь ход монстра!", reply_markup=ReplyKeyboardRemove())
        await Game.mob_move.set()
        await mob_attack(message)

@dp.message_handler(state = Game.mob_move)
async def mob_attack(message: types.Message):
    user_id = message.from_user.id
    cur_user = cur.session.execute(select(db.Person).where(db.Person.user_id == user_id)).scalar_one()
    mob_attack_type = "Физическая атака"
    damage_to_person = max(0, selected_mob.attack - cur_user.armour)
    if selected_mob.attack_type == "magical":
        damage_to_person = max(0, selected_mob.attack - cur_user.magic_armour)
        mob_attack_type = "Магическая атака"
    person_hp = max(0, cur_user.hp - damage_to_person)
    cur.session.query(db.Person).where(db.Person.user_id == user_id).update({"hp": person_hp})
    cur.session.commit()
    await message.answer(f"Удар монстра:  {mob_attack_type}\n"
                         f"Урон монстра вам: {damage_to_person}\n"
                         f"Ваше HP: {person_hp}\n")
    if cur_user.hp - damage_to_person <= 0:
        db.create_person(cur.session, cur_user.nickname, user_id)
        await message.answer(f"Очень сожалею, но монстр вас победил(. Вы возродитесь в городе с полным обнулением всех плюшек")
        await Game.in_city.set()
        await message.answer(text=f"Добро пожаловать, {cur_user.nickname}!")
        await message.answer("Вы переместились в город: Цитадель", reply_markup=in_city_keyboard)
    else:
        global job
        job = scheduler.add_job(lose_in_one_minute, "date", run_date=datetime.now() + timedelta(seconds=60),
                                args=[user_id, message])
        await message.answer("Ваш ход!", reply_markup=fight_keyboard)
        await Game.person_move.set()