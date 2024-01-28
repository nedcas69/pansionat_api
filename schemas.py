from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class RoomAvailability(BaseModel):
    date_start: date
    date_end: date


class OrderCreated(BaseModel):
    room_id: int
    fio: str
    guest_type: Optional[str]
    tel: str
    date_start: date
    date_end: date
    tabel: str
    user_id: int
    room_number: int
    room_class: str
    work: bool
    paytype: str
    pay_status: bool
    sebe_35: int
    pension_30: int
    semye_70: int
    commerc_100: int
    summa: int

class AdminCreated(BaseModel):
    room_id: int
    fio: str
    guest_type: Optional[str]
    zxcasd2356: Optional[str]
    tel: str
    date_start: date
    date_end: date
    tabel: str
    user_id: int
    room_number: int
    room_class: str
    work: bool
    paytype: str
    pay_status: bool
    sebe_35: int
    pension_30: int
    semye_70: int
    commerc_100: int
    summa: int


class OrderGet(BaseModel):
    room_id: int
    fio: str
    tel: str
    date_start: date
    date_end: date
    tabel: str
    user_id: int
    room_number: int
    room_class: str
    work: bool
    paytype: str
    pay_status: bool
    sebe_35: int
    pension_30: int
    semye_70: int
    commerc_100: int
    summa: int


class RoomCreate(BaseModel):
    number: str
    number_of_seats: int
    room_category: str


class Users(BaseModel):
    id: int
    fio: str
    role: Optional[str] = ''
    hashed_password: str
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    created_at: Optional[datetime]


class UsersCreate(BaseModel):
    fio: str
    hashed_password: str


class UserBase(BaseModel):
    username: str

