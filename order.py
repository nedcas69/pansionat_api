import math

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

order_router = APIRouter()
# Шаблонизатор Jinja2 для работы с HTML
templates = Jinja2Templates(directory="templates")


@order_router.get("/admin/orders/", response_class=HTMLResponse, name="admin_page")
async def admin_page(request: Request,
                     current_user: dict = Depends(get_current_user_from_cookie),
                     db: async_session = Depends(get_db)
                     ):
    user = get_user(current_user.get("username"), db)
    if not user:
        redirect_url = request.url_for("show_login_form")
        return RedirectResponse(url=redirect_url)

    redirect_url = f"/admin/orders/1"  # Замените на ваш URL
    raise HTTPException(status_code=303, detail="See Other", headers={"Location": redirect_url})


@order_router.post("/admin/orders/", name="_admin_page", response_model=dict)
async def admin_page1(request: Request,
                      current_user: dict = Depends(get_current_user_from_cookie),
                      db: async_session = Depends(get_db)
                      ):
    user = get_user(current_user.get("username"), db)
    if not user:
        redirect_url = request.url_for("show_login_form")
        return RedirectResponse(url=redirect_url)

    redirect_url = f"/admin/orders/1"  # Замените на ваш URL
    raise HTTPException(status_code=303, detail="See Other", headers={"Location": redirect_url})


@order_router.post("/admin/order/", name="_admin_page", response_model=dict)
async def admin_page1(request: Request,
                      page: Optional[int] = Form(...),
                      fio_order: Optional[str] = Form(...),
                      ids: Optional[int] = Form(...),
                      db: async_session = Depends(get_db),
                      current_user: dict = Depends(get_current_user_from_cookie)
                      ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user(current_user.get("username"), db)
    if not user:
        redirect_url = request.url_for("show_login_form")
        return RedirectResponse(url=redirect_url)
    id = ids
    querys = select(Order)
    try:
        if int(id):
            query = querys.where(Order.order_id == int(id))
            orders = await db.execute(query)
            order = orders.scalar()
            if order.work:
                # Обновляем флаг work на False
                order.work = False
            else:
                order.work = True
            print('-----------------------------------------ok-----------------')
            await db.commit()

    except Exception as e:
        # Обработка ошибок, например, вывод в лог
        print({"error": str(e)})
    fio = fio_order
    redirect_url = f"/admin/orders/{page}?fio_order={fio}"  # Замените на ваш URL
    raise HTTPException(status_code=303, detail="See Other", headers={"Location": redirect_url})


# Роут для отображения админки
@order_router.get("/admin/rooms/", response_class=HTMLResponse, name="show_admin_room", response_model=dict)
async def show_admin_room(request: Request,
                          date_start: Optional[date] = None,
                          date_end: Optional[date] = None,
                          current_user: dict = Depends(get_current_user_from_cookie),
                          db: async_session = Depends(get_db),
                          ):
    user = current_user.get("username")
    current_user = get_user(user, db)
    if not current_user:
        # redirect_url = "/login"
        redirect_url = request.url_for("show_login_form")
        return RedirectResponse(url=redirect_url)


# Роут для отображения админки
@order_router.get("/admin/orders/{page}", response_class=HTMLResponse, name="show_admin_page", response_model=dict)
async def show_admin_page(request: Request, page: int, fio_order: Optional[str] = None,
                          ids: Optional[int] = Form(None),
                          date_start: Optional[date] = None,
                          date_end: Optional[date] = None,
                          current_user: dict = Depends(get_current_user_from_cookie),
                          db: async_session = Depends(get_db),
                          ):
    user = current_user.get("username")
    current_user = get_user(user, db)
    if not current_user:
        # redirect_url = "/login"
        redirect_url = request.url_for("show_login_form")
        return RedirectResponse(url=redirect_url)


    try:
        per_page = 20
        pagination = True
        # Построение запроса для фильтрации
        query = select(Order)

        try:
            if int(fio_order):
                query = query.where(Order.tabel == str(fio_order))
                pagination = False

        except:
            try:
                pagination = False
                if fio_order and fio_order != 'None':
                    query = query.filter(Order.fio == fio_order)
                elif fio_order == 'None':
                    redirect_url = f'/admin/orders/{page}'  # Замените "show_login_form" на имя вашего роута с формой аутентификации
                    return RedirectResponse(url=redirect_url)

            except:
                pass
        try:
            if date_start and date_end:
                query = query.where(
                    (Order.date_start <= date_start) & (Order.date_end >= date_end) |
                    (Order.date_end >= date_start) & (Order.date_start <= date_end)
                )
                pagination = False
        except:
            if date_end == None and date_start == None:
                redirect_url = f'/admin/orders/{page}'
                return RedirectResponse(url=redirect_url)

        if pagination:
            query = select(Order).limit(per_page).offset((page - 1) * per_page)
        # Выполнение запроса
        orders = await db.execute(query)
        orders = orders.scalars().all()
        # Получение общего количества заказов для пагинации
        total_orders = await db.execute(select(func.count(Order.order_id)))
        total_orders = total_orders.scalar()
        total_pages = math.ceil(total_orders / per_page)
        total_sum = sum(order.summa for order in orders)
        id = ids
        querys = select(Order)
        try:
            if id:
                querys = querys.where(Order.order_id == id)
                order = await db.execute(querys)
                order = order.scalar()
                if order.work:
                    # Обновляем флаг work на False
                    order.work = False
                else:
                    order.work = True
                print('-----------------------------------------ok-----------------')
                await db.commit()
        except Exception as e:
            # Обработка ошибок, например, вывод в лог
            print(f"Error: {e}")

        return templates.TemplateResponse(
            "orders.html",
            {"request": request, "orders": orders, "current_page": page, "current_page_plus": page + 1,
             "current_page_minus": page - 1, "total_pages": total_pages,
             "username": user,
             "fio_order": fio_order, "pagination": pagination, "total_sum": total_sum},
        )

    except Exception as e:
        # Обработка ошибок, например, вывод в лог
        print(f"Error: {e}")