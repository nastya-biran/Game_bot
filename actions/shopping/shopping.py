from main import cur, Game, in_city_keyboard, section_keyboard, dp
from actions.inventory.inventory import change_item_activity
from aiogram import types
from aiogram.dispatcher.filters import Text
from sqlalchemy import select, delete, and_
import db


@dp.message_handler(Text(["Пойти в магазин"]), state = Game.in_city)
async def to_shop(message: types.Message):
    await Game.in_shop.set()
    await message.answer(f"Выберите раздел магазина", reply_markup=section_keyboard)

@dp.message_handler(Text(["Оружие","Броня и амуниция","Зелья"]), state = [Game.in_shop, Game.in_shop_weapon, Game.in_shop_armour,
                                                               Game.in_shop_potion, Game.select_item_to_sale,
                                                               Game.select_num_items_to_sale])
async def to_shop_section(message: types.Message):
    if message.text == "Оружие":
        await Game.in_shop_weapon.set()
        category = "weapon"
    elif message.text == "Броня и амуниция":
        await Game.in_shop_armour.set()
        category = "armour"
    else:
        await Game.in_shop_potion.set()
        category = "potion"
    user_id = message.from_user.id
    cur_loc_id = cur.session.query(db.Person).get(user_id).location_id
    items_in_shop = cur.session.execute(select(db.ItemsOnSale).where(db.ItemsOnSale.location_id == cur_loc_id)).scalars().all()
    answer_text = f"Товары в категории {message.text}: \n"
    count = 1
    global available_items_in_shop
    available_items_in_shop = []
    for item in items_in_shop:
        full_item = cur.session.query(db.Items).get(item.item_id)
        if full_item.item_type == category:
            available_items_in_shop.append(full_item.item_id)
            answer_text += str(count) + "." + str(full_item) + "\n"
            count += 1
    if answer_text == f"Товары в категории {message.text}: \n":
        answer_text += "Товары отсутствуют"
    await message.answer(answer_text)
    await message.answer("Для покупки введите номер товара")


@dp.message_handler(Text(["Выйти из магазина"]),  state = [Game.in_shop, Game.in_shop_weapon, Game.in_shop_armour,
                                                               Game.in_shop_potion, Game.select_item_to_sale,
                                                               Game.select_num_items_to_sale])
async def leave_store(message: types.Message):
    await Game.in_city.set()
    await message.answer("Вы вышли из магазина", reply_markup=in_city_keyboard)


@dp.message_handler(regexp=r"[\d]+", state=[Game.in_shop, Game.in_shop_weapon, Game.in_shop_armour, Game.in_shop_potion])
async def buy_item(message: types.Message):
    selected_item_num = int(message.text)
    user_id = message.from_user.id
    if selected_item_num> len(available_items_in_shop):
        await message.answer(f"Такого товара в данном разделе нет!", reply_markup=section_keyboard)
    else:
        item_id = available_items_in_shop[selected_item_num - 1]
        full_item = cur.session.query(db.Items).get(item_id)
        item_cost = full_item.cost
        money_on_hands = cur.session.query(db.Person).get(user_id).money
        if money_on_hands < item_cost:
            await message.answer(f"Вам не хватает денег!", reply_markup=section_keyboard)
        elif full_item.req_level > cur.session.query(db.Person).get(user_id).level:
            await message.answer(f"Вышего уровня недостаточно для покупки!", reply_markup=section_keyboard)
        else:
            await message.answer(f"Вы приобрели: {full_item.name}")
            await message.answer(f"Ваше оставшееся количество монет: {money_on_hands - item_cost}", reply_markup=section_keyboard)
            cur.session.query(db.Person).where(db.Person.user_id == user_id).update(
                {'money': money_on_hands - item_cost})
            cur.session.commit()
            items_in_persons_stock = cur.session.execute(
                select(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_id)).scalar_one_or_none()
            if items_in_persons_stock is not None:
                cur.session.query(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_id).update(
                    {'count': db.Stock.count + 1})
            else:
                new_item = db.Stock(user_id=user_id, item_id=item_id, count=1, is_on=False)
                cur.session.add(new_item)
            cur.session.commit()

@dp.message_handler(Text(["Продать свой инвентарь"]), state = [Game.in_shop, Game.in_shop_weapon, Game.in_shop_armour,
                                                               Game.in_shop_potion])
async def sell_to_shop(message: types.Message):
    user_id = message.from_user.id
    available_inventory = cur.session.execute(select(db.Stock).where(db.Stock.user_id == user_id)).scalars().all()
    answer_text = "Инвентарь, доступный для продажи: \n"
    global available_items_to_sale
    available_items_to_sale = []
    i = 0
    for item in available_inventory:
        i += 1
        full_item = cur.session.query(db.Items).get(item.item_id)
        available_items_to_sale.append(item.item_id)
        answer_text += str(i) + "."
        answer_text += f"Название: {full_item.name}\n" \
                       f"Цена продажи: {full_item.cost_to_sale}\n" \
                       f"Имеющееся количество: {item.count}\n"
    if answer_text == "Инвентарь, доступный для продажи: \n":
        answer_text += "Нет товаров ля продажи"
        await message.answer(answer_text, reply_markup=section_keyboard)
    else:
        await message.answer(answer_text)
        await message.answer(f"Для продажи введите номер предмета", reply_markup=section_keyboard)
    await Game.select_item_to_sale.set()

@dp.message_handler(regexp=r"[\d]+", state = Game.select_item_to_sale)
async def select_item_to_sale(message: types.Message):
    item_ind = int(message.text)
    if item_ind > len(available_items_to_sale):
        await message.answer(f"У вас нет такого предмета в инвентаре!", reply_markup=section_keyboard)
    else:
        item_id = available_items_to_sale[item_ind - 1]
        global item_to_sale_id
        item_to_sale_id = item_id
        await message.answer(f"Введите количество товара, которое хотите продать")
        await Game.select_num_items_to_sale.set()

@dp.message_handler(regexp=r"[\d]+", state = Game.select_num_items_to_sale)
async def select_num_items_to_sale(message: types.Message):
    user_id = message.from_user.id
    item_num = int(message.text)
    full_item = cur.session.query(db.Items).get(item_to_sale_id)
    available_num = cur.session.execute(select(db.Stock.count).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_to_sale_id)).scalar_one_or_none()
    if available_num < item_num:
        await message.answer(f"В инвентаре не достаточно предметов данного типа")
    else:
        items_left = cur.session.execute(select(db.Stock.count).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_to_sale_id)).scalar_one()
        cur.session.query(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_to_sale_id).update(
            {'count': db.Stock.count - item_num})
        cur.session.commit()
        if items_left == 1:
            if cur.session.execute(select(db.Stock.is_on).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_to_sale_id)).scalar_one() is True:
                await change_item_activity(user_id, item_to_sale_id, False)
            cur.session.execute(delete(db.Stock).where(db.Stock.user_id == user_id).where(db.Stock.item_id == item_to_sale_id))
        cur.session.query(db.Person).where(db.Person.user_id == user_id).update({'money': db.Person.money + item_num * full_item.cost_to_sale})
        cur.session.commit()
        answer_text = f"Вы продали: {full_item.name}\n" \
                      f"Количество проданных экземпляров: {item_num}\n" \
                      f"Полученные деньги: {item_num * full_item.cost_to_sale}\n"
        await message.answer(answer_text, reply_markup=section_keyboard)
    await Game.in_shop.set()
    await sell_to_shop(message)