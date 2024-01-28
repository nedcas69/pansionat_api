import math
import datetime as dates
from collections import defaultdict
from datetime import timedelta
from fastapi import status, APIRouter, Depends, Form, HTTPException
from sqlalchemy import func
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from starlette.templating import Jinja2Templates

from auth import get_user, get_current_user_from_cookie
from schemas import *
from models import *
from db import async_session, get_db

room_router = APIRouter()
# Шаблонизатор Jinja2 для работы с HTML
templates = Jinja2Templates(directory="templates")


 # Роут для отображения админки
@room_router.get("/admin/rooms/", response_class=HTMLResponse, name="show_admin_room", response_model=dict)
async def show_admin_room(request: Request,
                          date_start: Optional[date] = None,
                          date_end: Optional[date] = None,
                          current_user: dict = Depends(get_current_user_from_cookie),
                          db: async_session = Depends(get_db),
                          ):
    user = current_user.get("username")
    current_user = get_user(user, db)
    if current_user == '0':
        redirect_url = "/login"
        # redirect_url = request.url_for("show_login_form")
        return RedirectResponse(url=redirect_url)

    try:
        # Построение запроса для фильтрации
        querys = select(Order)
        try:
            if date_start and date_end:
                querys = querys.where(
                    (Order.date_start <= date_start) & (Order.date_end >= date_end) |
                    (Order.date_end >= date_start) & (Order.date_start <= date_end)
                )
        except:
            pass
        # Построение запроса для фильтрации
        query = select(Room)
        # Выполнение запроса
        orders = await db.execute(querys)
        orders = orders.scalars().all()
        rooms = await db.execute(query)
        rooms = rooms.scalars().all()
        # Преобразовываем orders в JSON
        json_data = []
        orders_by_room = defaultdict(list)

        # Группируем заказы по room_id
        for order in orders:
            orders_by_room[order.room_id].append(order)
        for room in rooms:
            room_toDict={}
            room_toDict['status'] = room.status
            room_toDict['number'] = room.number
            room_toDict['number_of_seats'] = room.number_of_seats
            room_toDict['room_category'] = room.room_category
            room_toDict['one'] = ''
            room_toDict['two'] = ''
            room_toDict['three'] = ''
            room_orders = orders_by_room.get(room.id, [])
            # Обходим заказы для текущей комнаты
            for i, order in enumerate(room_orders):
                if i == 0:
                    room_toDict['one'] = order.fio
                elif i == 1:
                    room_toDict['two'] = order.fio
                elif i == 2:
                    room_toDict['three'] = order.fio
            json_data.append(room_toDict)
        return templates.TemplateResponse(
            "rooms.html",
            {"request": request, "rooms": json_data},
        )

    except Exception as e:
        # Обработка ошибок, например, вывод в лог
        print(f"Error: {e}")