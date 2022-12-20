from db import Person, Mobs, Locations, Items, ItemsOnSale, Base, engine
import random

def init_mobs(session):
    default_mobs = []
    default_mobs.append(
        Mobs(name="Берсерк", hp=10, xp=10, req_level=1, attack_type="physical", attack=3, armour=3, magic_armour=0))
    default_mobs.append(
        Mobs(name="Циклоп", hp=8, xp=8, req_level=1, attack_type="physical", attack=4, armour=4,
             magic_armour=0))
    default_mobs.append(
        Mobs(name="Гаргулья", hp=7, xp=10, req_level=1, attack_type="magical", attack=5, armour=2,
             magic_armour=1))

    default_mobs.append(
        Mobs(name="Доплер", hp=13, xp=15, req_level=2, attack_type="physical", attack=9, armour=7, magic_armour=4))
    default_mobs.append(
        Mobs(name="Стрыга", hp=15, xp=20, req_level=2, attack_type="magical", attack=7, armour=5, magic_armour=5))
    default_mobs.append(
        Mobs(name="Кикимора", hp=17, xp=25, req_level=2, attack_type="magical", attack=12, armour=7, magic_armour=3))

    default_mobs.append(
        Mobs(name="Волколак", hp=20, xp=30, req_level=3, attack_type="physical", attack=13, armour=9, magic_armour=6))
    default_mobs.append(
        Mobs(name="Упырь", hp=28, xp=25, req_level=3, attack_type="physical", attack=17, armour=7, magic_armour=8))
    default_mobs.append(
        Mobs(name="Брукса", hp=20, xp=35, req_level=3, attack_type="magical", attack=25, armour=5, magic_armour=10))

    default_mobs.append(
        Mobs(name="Голем", hp=30, xp=40, req_level=4, attack_type="magical", attack=18, armour=8, magic_armour=13))
    default_mobs.append(
        Mobs(name="Леший", hp=35, xp=45, req_level=4, attack_type="magical", attack=20, armour=6, magic_armour=12))
    default_mobs.append(
        Mobs(name="Чернобог", hp=40, xp=50, req_level=4, attack_type="physical", attack=22, armour=5, magic_armour=2))

    default_mobs.append(
        Mobs(name="Дракон", hp=60, xp=70, req_level=5, attack_type="physical", attack=25, armour=15, magic_armour=20))
    default_mobs.append(
        Mobs(name="Василиск", hp=70, xp=90, req_level=5, attack_type="physical", attack=30, armour=18, magic_armour=13))
    default_mobs.append(
        Mobs(name="Котолак", hp=65, xp=80, req_level=5, attack_type="magical", attack=28, armour=16, magic_armour=22))
    session.add_all(default_mobs)
    session.commit()

def init_locations(session):
    default_locations = []
    default_locations.append(Locations(location_id=1, name="Цитадель", x_coord=1, y_coord=1, loc_type="city"))
    default_locations.append(Locations(location_id=2, name="Аден", x_coord=7, y_coord=5, loc_type="city"))
    default_locations.append(Locations(location_id=3, name="Боклер", x_coord=9, y_coord=10, loc_type="city"))
    default_locations.append(Locations(location_id=4, name="Блавикен", x_coord=13, y_coord=12, loc_type="city"))
    default_locations.append(Locations(location_id=5, name="Ривия", x_coord=16, y_coord=15, loc_type="city"))
    default_locations.append(
        Locations(location_id=6, name="Кровавые катакомбы", x_coord=2, y_coord=3, loc_type="dungeon"))
    default_locations.append(
        Locations(location_id=7, name="Театр Боли", x_coord=6, y_coord=5, loc_type="dungeon"))
    default_locations.append(
        Locations(location_id=8, name="Чертоги покаяния", x_coord=10, y_coord=15, loc_type="dungeon"))
    default_locations.append(
        Locations(location_id=9, name="Смертельная тризна", x_coord=17, y_coord=16, loc_type="dungeon"))
    default_locations.append(
        Locations(location_id=10, name="Та сторона", x_coord=20, y_coord=19, loc_type="dungeon"))
    session.add_all(default_locations)
    session.commit()

def init_items(session):
    default_items = []
    default_items.append(Items(cost=5, cost_to_sale=3, item_type="weapon", hp=0, mana=0, attack=7,
                               magic_attack=0, armour=0, magic_armour=0, req_level=1, name="Легкая дубинка"))
    default_items.append(Items(cost=3, cost_to_sale=1, item_type="weapon", hp=0, mana=0, attack=5,
                               magic_attack=1, armour=0, magic_armour=0, req_level=1, name="Двуручный стальной топор"))
    default_items.append(Items(cost=6, cost_to_sale=4, item_type="weapon", hp=0, mana=0, attack=3,
                               magic_attack=7, armour=0, magic_armour=0, req_level=1, name="Кинжал убийцы"))

    default_items.append(Items(cost=10, cost_to_sale=5, item_type="weapon", hp=0, mana=0, attack=10,
                               magic_attack=5, armour=0, magic_armour=0, req_level=2, name="Маленький топор"))
    default_items.append(Items(cost=8, cost_to_sale=5, item_type="weapon", hp=0, mana=0, attack=12,
                               magic_attack=7, armour=0, magic_armour=0, req_level=2, name="Плеть"))
    default_items.append(Items(cost=11, cost_to_sale=7, item_type="weapon", hp=0, mana=0, attack=6,
                               magic_attack=10, armour=0, magic_armour=0, req_level=2, name="Серебряный меч"))

    default_items.append(Items(cost=15, cost_to_sale=11, item_type="weapon", hp=0, mana=0, attack=15,
                               magic_attack=8, armour=0, magic_armour=0, req_level=3, name="Цепная булава"))
    default_items.append(Items(cost=13, cost_to_sale=8, item_type="weapon", hp=0, mana=0, attack=13,
                               magic_attack=9, armour=0, magic_armour=0, req_level=3, name="Каменный молот"))
    default_items.append(Items(cost=18, cost_to_sale=10, item_type="weapon", hp=0, mana=0, attack=18,
                               magic_attack=12, armour=0, magic_armour=0, req_level=3, name="Тяжелая булава"))

    default_items.append(Items(cost=18, cost_to_sale=16, item_type="weapon", hp=0, mana=0, attack=18,
                               magic_attack=10, armour=0, magic_armour=0, req_level=4, name="Стальной меч"))
    default_items.append(Items(cost=20, cost_to_sale=12, item_type="weapon", hp=0, mana=0, attack=19,
                               magic_attack=14, armour=0, magic_armour=0, req_level=4, name="Меч ордена"))
    default_items.append(Items(cost=22, cost_to_sale=15, item_type="weapon", hp=0, mana=0, attack=25,
                               magic_attack=18, armour=0, magic_armour=0, req_level=4, name="Топор краснолюдов"))

    default_items.append(Items(cost=25, cost_to_sale=20, item_type="weapon", hp=0, mana=0, attack=20,
                               magic_attack=25, armour=0, magic_armour=0, req_level=5, name="Двуручный моргенштерн"))





    default_items.append(Items(cost=3, cost_to_sale=1, item_type="armour", hp=0, mana=0, attack=0,
                               magic_attack=0, armour=5, magic_armour=0, req_level=1, name="Военная кожаная куртка"))
    default_items.append(Items(cost=7, cost_to_sale=4, item_type="armour", hp=0, mana=0, attack=0,
                               magic_attack=0, armour=10, magic_armour=0, req_level=2, name="Расшитый кунтуш"))
    default_items.append(Items(cost=12, cost_to_sale=7, item_type="armour", hp=0, mana=0, attack=0,
                               magic_attack=0, armour=16, magic_armour=4, req_level=3, name="Доспех ласточки"))
    default_items.append(Items(cost=12, cost_to_sale=7, item_type="armour", hp=0, mana=0, attack=0,
                               magic_attack=0, armour=20, magic_armour=8, req_level=4, name="Доспех ласточки"))
    default_items.append(Items(cost=17, cost_to_sale=10, item_type="armour", hp=0, mana=0, attack=0,
                               magic_attack=0, armour=23, magic_armour=13, req_level=4, name="Доспех Тиссена"))
    default_items.append(Items(cost=20, cost_to_sale=10, item_type="armour", hp=0, mana=0, attack=0,
                               magic_attack=0, armour=27, magic_armour=18, req_level=5, name="Доспех школы волка"))





    default_items.append(Items(cost=3, cost_to_sale=0, item_type="potion", hp=3, mana=1, attack=0,
                               magic_attack=0, armour=0, magic_armour=5, req_level=1, name="Эликсир Петри"))
    session.add_all(default_items)
    default_items.append(Items(cost=7, cost_to_sale=0, item_type="potion", hp=8, mana=1, attack=0,
                               magic_attack=0, armour=3, magic_armour=9, req_level=1, name="Черная кровь"))
    default_items.append(Items(cost=10, cost_to_sale=0, item_type="potion", hp=15, mana=1, attack=0,
                               magic_attack=0, armour=8, magic_armour=12, req_level=2, name="Эликсир очищения"))
    session.add_all(default_items)
    session.commit()

def init_sales(session):
    default_sales = []
    for i in range (1, 6):
        num = random.randint(7, 13)
        s = set()
        row_num = session.query(Items).count()
        for j in range(0, num):
            item_id = random.randint(1, row_num)
            if item_id in s:
                continue
            s.add(item_id)
            default_sales.append(ItemsOnSale(location_id=i, item_id=item_id))
    session.add_all(default_sales)
    session.commit()

def init_db(session):
    Base.metadata.create_all(engine)
    init_mobs(session)
    init_locations(session)
    init_items(session)
    init_sales(session)