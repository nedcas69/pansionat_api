import math
import datetime as dates
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
        per_page = 1000
        pagination = False
        # Построение запроса для фильтрации
        query = select(Room)

        return templates.TemplateResponse(
            "rooms.html",
            {"request": request, },
        )

    except Exception as e:
        # Обработка ошибок, например, вывод в лог
        print(f"Error: {e}")