from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

engine = create_engine("sqlite+pysqlite:///game.db", echo=True)

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'

    user_id = Column(Integer, name='UserId', primary_key=True)
    nickname = Column(String)
    level = Column(Integer)
    hp = Column(Integer)
    cur_hp = Column(Integer)
    money = Column(Integer)
    attack = Column(Integer)
    magic_attack = Column(Integer)
    xp = Column(Integer)
    armour = Column(Integer)
    magic_armour = Column(Integer)
    location_id = Column(Integer)

    def __repr__(self):
        s = f"Уровень: {self.level} \n" \
            f"Здоровье: {self.cur_hp}\n" \
            f"Деньги: {self.money} \n" \
            f"Атака: {self.attack} \n" \
            f"Магическая атака: {self.magic_attack} \n" \
            f"Опыт: {self.xp} \n" \
            f"Броня: {self.armour}\n" \
            f"Магическая броня: {self.magic_armour} \n\n"
        return s

class Mobs(Base):
    __tablename__ = 'mobs'

    mob_id = Column(Integer, name='MobId', primary_key=True)
    name = Column(String)
    hp = Column(Integer)
    xp = Column(Integer)
    req_level = Column(Integer)
    attack_type = Column(String)
    attack = Column(Integer)
    armour = Column(Integer)
    magic_armour = Column(Integer)

    def __repr__(self):
        s = f"Название: {self.name}\n" \
            f"HP: {self.hp}\n" \
            f"XP: {self.xp}\n" \
            f"Требуемый уровень: {self.req_level}\n" \
            f"Тип атаки: {self.attack_type}\n" \
            f"Атака: {self.attack}\n" \
            f"Броня: {self.armour}\n" \
            f"Магическая броня: {self.magic_armour}\n\n"
        return s


class Locations(Base):
    __tablename__ = "locations"

    location_id = Column(Integer, name="LocId", primary_key=True)
    name = Column(String)
    x_coord = Column(Integer)
    y_coord = Column(Integer)
    loc_type = Column(String)

    def __repr__(self):
        s = f"Название: {self.name}\n" \
            f"Координаты: {self.x_coord}, {self.y_coord}\n"
        return s


class Items(Base):
    __tablename__ = "items"

    item_id = Column(Integer, name="ItemId", primary_key=True)
    name = Column(String)
    cost = Column(Integer)
    cost_to_sale = Column(Integer)
    item_type = Column(String)
    hp = Column(Integer)
    mana = Column(Integer)
    attack = Column(Integer)
    magic_attack = Column(Integer)
    armour = Column(Integer)
    magic_armour = Column(Integer)
    req_level = Column(Integer)

    def __repr__(self):
        s = f"Название: {self.name}\n" \
            f"Стоимость: {self.cost}\n" \
            f"Стоимость продажи: {self.cost_to_sale}\n" \
            f"Дополнительное здоровье: {self.hp}\n" \
            f"Дополнительная мана: {self.mana}\n" \
            f"Атака: {self.attack}\n" \
            f"Магическая атака: {self.magic_attack}\n" \
            f"Броня: {self.armour}\n" \
            f"Магическая броня: {self.magic_armour}\n" \
            f"Требуемый уровень: {self.req_level}\n\n"
        return s


class ItemsOnSale(Base):
    __tablename__ = "sale"

    id = Column(Integer, name="SaleId", primary_key=True)
    location_id = Column(Integer)
    item_id = Column(Integer)

    def __repr__(self):
        s = f"location_id : {self.location_id}\n" \
            f"item_id: {self.item_id}\n\n"
        return s

class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, name="StockId", primary_key=True)
    user_id = Column(Integer)
    item_id = Column(Integer)
    count = Column(Integer)
    is_on = Column(Boolean)

    def __repr__(self):
        s = f"user_id: {self.user_id}\n" \
            f"item_id: {self.item_id}\n" \
            f"count: {self.count}\n" \
            f"is_on: {self.is_on}\n\n"
        return s


def create_person(session, nickname, user_id):
    new_person = Person(user_id=user_id, nickname=nickname, level=1, hp=100, cur_hp=100, money=20, attack=2, magic_attack=2, xp=0, armour=2, magic_armour=2, location_id=1)
    res = session.query(Person).get(user_id)
    print(type(res))
    print(res)
    if res is not None:
        session.execute(delete(Person).where(Person.user_id == user_id))
        session.execute(delete(Stock).where(Stock.user_id == user_id))
        session.commit()
    session.add(new_person)
    session.commit()


class MySession():
    def __init__(self):
        Session = sessionmaker(bind=engine, future=True, expire_on_commit=False)
        self.session = Session()




