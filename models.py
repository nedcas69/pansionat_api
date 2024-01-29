from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger, Date, TIMESTAMP

from db import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    fio = Column(String)
    role = Column(String, default='--')
    hashed_password = Column(String)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class Order(Base):
    __tablename__ = "order"
    order_id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("room.id"))
    user_id = Column(BigInteger)
    fio = Column(String, nullable=False)
    tel = Column(String, nullable=False)
    room_number = Column(Integer)
    room_class = Column(String)
    work = Column(Boolean, default=False)
    date_start = Column(Date)
    date_end = Column(Date)
    tabel = Column(String)
    paytype = Column(String)
    pay_status = Column(Boolean, default=False)
    sebe_35 = Column(Integer)
    pension_30 = Column(Integer)
    semye_70 = Column(Integer)
    commerc_100 = Column(Integer)
    summa = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)


# Определяем модель для таблицы в базе данных Room
class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    number = Column(String, nullable=False)
    number_of_seats = Column(Integer, nullable=False)
    room_category = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    status = Column(Boolean, default=True)