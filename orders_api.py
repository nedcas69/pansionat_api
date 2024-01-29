import requests
from requests.auth import HTTPBasicAuth
from fastapi import Depends, APIRouter, Form, Request

from datetime import timedelta

from sqlalchemy import insert, func, select, desc

from schemas import *
from models import *
from config import C_USER, C_PASS, C_buh
from db import async_session, get_db

orderApi_router = APIRouter()


# Роут для создания заказа в базе данных
@orderApi_router.post("/orders")
async def create_order(order: OrderCreated, db: async_session = Depends(get_db)):
    try:
        guest_type = order.guest_type
        order.user_id = 0
        order.sebe_35 = 0
        order.pension_30 = 0
        order.semye_70 = 0
        order.commerc_100 = 0
        if guest_type == 'pen':
            order.pension_30 = 30
        if guest_type == 'sebe':
            order.sebe_35 = 35
        if guest_type == 'family':
            order.semye_70 = 70
        if guest_type == 'friend':
            order.commerc_100 = 100
        # async with engine.begin() as conn:
        rooms = await db.execute(Room.__table__.select().where(
            Room.id == order.room_id
        ))
        room = rooms.fetchone()
        order.room_number = int(room.number)
        order.room_class = room.room_category
        order.work = True
        order.paytype = 'Иш ҳақи ҳисобидан'
        order.pay_status = True
        lgots = order.sebe_35 + order.pension_30 + order.semye_70 + order.commerc_100
        summa = 0
        period = (order.date_end - order.date_start).days
        for i in range(period):
            if order.room_class == 'Lyuks':
                summa += (lgots / 100) * 414000
            if order.room_class == 'Standart':
                summa += (lgots / 100) * 276000

        order.summa = summa
        # async with engine.begin() as conn:
        orders = await db.execute(
            Order.__table__.select().where(
                (Order.date_start <= order.date_start) & (
                        Order.date_end >= order.date_start + timedelta(days=1)) & (Order.pay_status == True) |
                (Order.date_start <= order.date_end - timedelta(days=1)) & (
                        Order.date_end >= order.date_end) & (Order.pay_status == True))
        )
        ordersxh = []
        orders = orders.fetchall()
        if order.fio != "Boshqa insonga":
            ordersx = await db.execute(
                Order.__table__.select().where(
                    (Order.date_start == order.date_start) & (
                            Order.date_end == order.date_end) & (Order.fio == order.fio))
            )
            ordersxh = ordersx.fetchall()
        # Если уже есть заказы с подобными параметрами, возвращаем False

        orders_of_seats = 0
        for orderz in orders:
            if order.room_id == orderz.room_id:
                orders_of_seats += 1

        if orders_of_seats < room.number_of_seats and summa != 0 and ordersxh == []:
            # Создаем словарь из экземпляра модели, исключив атрибут 'guest_type'
            obj_dict = order.dict(exclude={'guest_type'})

            # Создаем объект модели Order для записи в базу данных
            roomType = 0
            if order.room_class == 'Standart':
                roomType = 1
            if order.room_class == 'Lyuks':
                return False

            paymentType = 0
            if order.sebe_35 != 0:
                paymentType = 1
            if order.pension_30 != 0:
                paymentType = 4
            if order.semye_70 != 0:
                paymentType = 2
            if order.commerc_100 != 0:
                paymentType = 3
            start = str(order.date_start.strftime('%Y%m%d'))
            end = str(order.date_end.strftime('%Y%m%d'))
            data = {
                "tabNomer": order.tabel,
                "period1": start,
                "period2": end,
                "roomType": roomType,
                "paymentType": paymentType,
                "vacationer": order.fio
            }

            auth = HTTPBasicAuth(C_USER, C_PASS)
            r = requests.post(C_buh, auth=auth, json=data)
            if r.status_code == 201:
                db_order = Order(**obj_dict)

                # Соединяемся с базой данных и добавляем заказ
                # async with async_session() as session:
                if True:
                    db.add(db_order)
                    await db.commit()

                return db_order
            else:
                return False
        else:
            return False
    except:
        return False


# Роут для выполнения задачи
@orderApi_router.post("/calculate")
async def calculate_stats(date_range: RoomAvailability, db: async_session = Depends(get_db)):
    # Подключаемся к базе данных
    # async with engine.begin() as conn:
    try:
        # Получаем все заказы, которые входят в заданный временной интервал
        orders = await db.execute(
            Order.__table__.select().where(
                (Order.date_start <= date_range.date_start) & (
                        Order.date_end >= date_range.date_start + timedelta(days=1)) & (Order.pay_status == True) |
                (Order.date_start <= date_range.date_end - timedelta(days=1)) & (
                        Order.date_end >= date_range.date_end) & (Order.pay_status == True))
        )
        orders = orders.fetchall()

        # Формируем словарь {"room_number": int, "количество ордеров на эту комнату за этот период": int, "room_class": str}
        room_stats = {}
        for order in orders:
            if order.pay_status:
                room_number = order.room_number
                room_class = order.room_class
                if room_number not in room_stats:
                    room_stats[room_number] = {"count": 0, "room_class": room_class}
                room_stats[room_number]["count"] += 1

        # Получаем все комнаты
        rooms = await db.execute(Room.__table__.select().where(Room.status == True))
        rooms = rooms.fetchall()

        # Формируем новый словарь {"room_number": int, "number_of_seats": int, "room_class": str}
        result = []
        for room in rooms:
            room_id = room.id
            room_number = room.number
            room_class = room.room_category
            number_of_seats = room.number_of_seats
            romsts = room_stats.get(int(room_number), {"count": 0})
            count = romsts["count"]
            available_seats = max(0, number_of_seats - count)
            if available_seats > 0:
                result.append({
                    "room_id": room_id,
                    "room_number": room_number,
                    "number_of_seat": number_of_seats,
                    "number_of_seats": available_seats,
                    "room_class": room_class
                })
        # import datetime
        # select_date = datetime.date(2024, 1, 8)
        # select_date_1 = datetime.date(2024, 1, 9)
        # select_date_2 = datetime.date(2024, 1, 10)
        # select_date_3 = datetime.date(2024, 1, 11)
        # select_date_end = datetime.date(2024, 1, 12)
        #
        # if date_range.date_start <= select_date <= date_range.date_end or \
        #         date_range.date_start <= select_date_1 <= date_range.date_end \
        #         or date_range.date_start <= select_date_2 <= date_range.date_end \
        #         or date_range.date_start <= select_date_3 <= date_range.date_end \
        #         or date_range.date_start <= select_date_end < date_range.date_end:
        #     return False
        # else:
        return result
    except:
        return False


@orderApi_router.post("/orders/admin")
async def create_order_admin(
        zxcasd2356: str = Form(),
        guest_type: str = Form(),
        tabel: str = Form(),
        fio: str = Form(),
        room_number: str = Form(),
        tel: str = Form(),
        date_start: Optional[date] = Form(),
        date_end: Optional[date] = Form(),
        db: async_session = Depends(get_db)):
    try:
        role = zxcasd2356
        print(role)
        guest_type = guest_type
        user_id = 0
        sebe_35 = 0
        pension_30 = 0
        semye_70 = 0
        commerc_100 = 0
        if role == 'admin':
            if guest_type == 'pen':
                pension_30 = 30
            if guest_type == 'sebe':
                sebe_35 = 35
            if guest_type == 'family':
                semye_70 = 70
            if guest_type == 'friend':
                commerc_100 = 100
        else:
            commerc_100 = 100
        # async with engine.begin() as conn:
        rooms = await db.execute(Room.__table__.select().where(
            Room.number == room_number
        ))
        room = rooms.fetchone()
        room_id = room.id
        room_class = room.room_category

        work = True
        paytype = 'Иш ҳақи ҳисобидан'
        pay_status = True
        lgots = sebe_35 + pension_30 + semye_70 + commerc_100
        summa = 0
        period = (date_end - date_start).days
        for i in range(period):
            if room_class == 'Lyuks':
                summa += (lgots / 100) * 414000
            if room_class == 'Standart':
                summa += (lgots / 100) * 276000

        summa = summa
        # async with engine.begin() as conn:
        orders = await db.execute(
            Order.__table__.select().where(
                (Order.date_start <= date_start) & (
                        Order.date_end >= date_start + timedelta(days=1)) & (Order.pay_status == True) |
                (Order.date_start <= date_end - timedelta(days=1)) & (
                        Order.date_end >= date_end) & (Order.pay_status == True))
        )
        ordersxh = []
        orders = orders.fetchall()
        if fio != "Boshqa insonga":
            ordersx = await db.execute(
                Order.__table__.select().where(
                    (Order.date_start == date_start) & (
                            Order.date_end == date_end) & (Order.fio == fio))
            )
            ordersxh = ordersx.fetchall()

        orders_of_seats = 0
        for orderz in orders:
            if room_id == orderz.room_id:
                orders_of_seats += 1

        if orders_of_seats < room.number_of_seats and summa != 0 and ordersxh == []:

            # Создаем объект модели Order для записи в базу данных
            roomType = 0
            if room_class == 'Standart':
                roomType = 1
            if room_class == 'Lyuks':
                roomType = 2

            paymentType = 0
            if sebe_35 != 0:
                paymentType = 1
            if pension_30 != 0:
                paymentType = 4
            if semye_70 != 0:
                paymentType = 2
            if commerc_100 != 0:
                paymentType = 3
            start = str(date_start.strftime('%Y%m%d'))
            end = str(date_end.strftime('%Y%m%d'))
            data = {
                "tabNomer": tabel,
                "period1": start,
                "period2": end,
                "roomType": roomType,
                "paymentType": paymentType,
                "vacationer": fio
            }

            orders = await db.execute(Order.__table__.select())
            orders = orders.fetchall()
            room_number = int(room_number)
            now = datetime.now()
            max_order_id = 1
            # print(orders)
            for ordern in orders:
                print(ordern.order_id)
                if ordern.order_id > max_order_id:
                    max_order_id = ordern.order_id
            new_order = max_order_id + 1
            print(role, )
            if role == "admin":
                auth = HTTPBasicAuth(C_USER, C_PASS)
                r = requests.post(C_buh, auth=auth, json=data)

                if r.status_code == 201:
                    result = await db.execute(insert(Order).values(
                        order_id=new_order, room_id=room_id, user_id=user_id, fio=fio, tel=tel,
                        room_number=room_number, room_class=room_class, work=work, date_start=date_start,
                        date_end=date_end, tabel=tabel, paytype=paytype, pay_status=pay_status, sebe_35=sebe_35,
                        pension_30=pension_30, semye_70=semye_70, commerc_100=commerc_100, summa=summa,
                        created_at=now, updated_at=now))

                    await db.commit()
                    return {"message": "Ваш заказ оформлен!", "err": '1'}
                else:
                    return {"message": "Возникла ошибка при соединении с 1С! Попробуйте заново", "err": '0'}
            elif role == "moder":
                result = await db.execute(insert(Order).values(
                    order_id=new_order, room_id=room_id, user_id=user_id, fio=fio, tel=tel,
                    room_number=room_number, room_class=room_class, work=work, date_start=date_start,
                    date_end=date_end, tabel=tabel, paytype=paytype, pay_status=pay_status, sebe_35=sebe_35,
                    pension_30=pension_30, semye_70=semye_70, commerc_100=commerc_100, summa=summa,
                    created_at=now, updated_at=now))

                await db.commit()
                return {"message": "Ваш заказ оформлен!", "err": '1'}
            else:
                return {"message": "У вас нет доступа", "err": '0'}
        else:
            return {"message": "Возникла ошибка! Такой заказ существует или комната заполнено.", "err": '0'}
    except:
        return {"message": "Возникла ошибка!", "err": '0'}


# Роут для отображения админки
@orderApi_router.get("/get_orders/{tabel}")
async def show_admin_page(tabel: Optional[str] = None,
                          db: async_session = Depends(get_db),
                          ):
    # Построение запроса для фильтрации
    orders = await db.execute(Order.__table__.select().where(Order.tabel == tabel))
    orders = orders.fetchall()
    send_data = []
    for order in orders:
        send_data.append({"fio": order.fio,
                          "date_start": order.date_start,
                          "date_end": order.date_end,
                          "summa": order.summa})
    return send_data
