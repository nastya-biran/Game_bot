from main import cur, Game, in_city_keyboard, inventory_keyboard, dp
from aiogram import  types
from aiogram.dispatcher.filters import Text
from sqlalchemy import select
import db


@dp.message_handler(Text(["Посмотреть свой инвентарь и поменять активный инвентарь"]), state = Game.in_city)
async def to_inventory(message: types.Message):
    user_id = message.from_user.id
    inventory = cur.session.execute(select(db.Stock).where(db.Stock.user_id == user_id)).scalars().all()
    answer_text = "Ваш инвентарь: \n"
    i = 0
    global available_inventory
    available_inventory = []
    for item in inventory:
        i += 1
        item_id = item.item_id
        available_inventory.append(item_id)
        full_item = cur.session.execute(select(db.Items).where(db.Items.item_id == item_id)).scalar_one()
        answer_text += str(i) + "." + str(full_item) + \
                       "\n" + "Количество: " + str(item.count) + "\n"
    if answer_text == "Ваш инвентарь: \n":
        answer_text += "Нет инвентаря"
    await message.answer(answer_text, reply_markup=inventory_keyboard)
    await Game.in_inventory.set()


@dp.message_handler(Text(["Выйти из инвентаря"]), state=[Game.in_inventory, Game.select_active_inventory])
async def leave_inventory(message: types.Message):
    await Game.in_city.set()
    await message.answer("Вы вышли из инвентаря", reply_markup=in_city_keyboard)


@dp.message_handler(Text(["Посмотреть активный инвентарь"]), state=[Game.in_inventory, Game.select_active_inventory])
async def show_active_inventory(message: types.Message):
    user_id = message.from_user.id
    active_inventory = cur.session.execute(select(db.Stock).filter(db.Stock.is_on.is_(True)).
                                           filter(db.Stock.user_id == user_id)).scalars().all()
    answer_text = "Ваш активный инвентарь: \n"
    i = 0
    for item in active_inventory:
        i += 1
        item_id = item.item_id
        full_item = cur.session.execute(select(db.Items).where(db.Items.item_id == item_id)).scalar_one()
        answer_text += str(i) + "." + full_item.name + "\n"
    if answer_text == "Ваш активный инвентарь: \n":
        answer_text += "Нет активного инвентаря"
    await message.answer(answer_text, reply_markup=inventory_keyboard)
    await Game.in_inventory.set()


@dp.message_handler(Text(["Изменить активный инвентарь"]), state = Game.in_inventory)
async def change_active_inventory(message: types.Message):
    await message.answer("Введите номер предмета из инвентаря, который хотели бы сделать активным", reply_markup=inventory_keyboard)
    await Game.select_active_inventory.set()

@dp.message_handler(regexp=r"[\d]+", state = Game.select_active_inventory)
async def select_active_inventory(message: types.Message):
    item_ind = int(message.text)
    user_id = message.from_user.id
    if item_ind > len(available_inventory):
        await message.answer("Такого предмета нет!")
        await Game.in_inventory.set()
        await change_active_inventory(message)
    else:
        item_id = available_inventory[item_ind - 1]
        full_item = cur.session.execute(select(db.Items).where(db.Items.item_id == item_id)).scalar_one()
        category = full_item.item_type
        if category != "potion":
            active_items = cur.session.execute(select(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.is_on.is_(True))).scalars().all()
            for active_item in active_items:
                active_item_id = active_item.item_id
                full_active_item = cur.session.execute(select(db.Items).where(db.Items.item_id == active_item_id)).scalar_one()
                if full_active_item.item_type == category:
                    await change_item_activity(user_id, active_item_id, False)
                    break
        await change_item_activity(user_id, item_id, True)
        await message.answer(f"Предмет {full_item.name} добавлен в активный инвентарь")
        await change_active_inventory(message)


async def change_item_activity(user_id, item_id, activate):
    mult = 1
    if  not activate:
        mult = -1
        cur.session.query(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_id).update(
            {'is_on': False})
    else:
        cur.session.query(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_id).update(
            {'is_on': True})
    full_item = cur.session.execute(select(db.Items).where(db.Items.item_id == item_id)).scalar_one()
    cur.session.query(db.Person).where(db.Person.user_id).update({'hp': db.Person.hp + mult * full_item.hp,
                                                                  'attack':  db.Person.attack + mult * full_item.attack,
                                                                  'magic_attack': db.Person.magic_attack + mult * full_item.magic_attack,
                                                                  'armour': db.Person.armour + mult * full_item.armour,
                                                                  'magic_armour': db.Person.magic_armour + mult * full_item.magic_armour})
    cur.session.commit()