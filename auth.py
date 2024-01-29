import math
import random

from fastapi import status, APIRouter, Depends, Form, HTTPException, Cookie, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy import func, insert
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from starlette.templating import Jinja2Templates
import logging
from starlette.responses import JSONResponse

from schemas import *
from models import *
from db import async_session, get_db

auth_router = APIRouter()

# Стандартные настройки для хэширования пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# Шаблонизатор Jinja2 для работы с HTML
templates = Jinja2Templates(directory="templates")

# Генерация зависимости для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Генерация токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return pwd_context.hash(password)


# Функция для получения пользователя из базы данных
async def get_user(username: str, db: async_session = Depends(get_db)):
    try:
        user = await db.execute(select(User).filter(User.fio == username))
        if user is None:
            # Обработка случая, когда пользователь не найден
            # Например, возбуждение исключения или возврат информации об отсутствии пользователя
            raise HTTPException(status_code=404, detail="Пользователь не найден.")
        return user.scalar()
    except:
        return "0"


# Функция для получения пользователя из базы данных
async def get_user_id(id: int, db: async_session = Depends(get_db)):
    user = await db.execute(select(User).filter(User.id == id))
    if user is None:
        # Обработка случая, когда пользователь не найден
        # Например, возбуждение исключения или возврат информации об отсутствии пользователя
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return user.scalar()


# Функция для проверки логина пользователя
async def verify_user(username: str, password: str, db: async_session = Depends(get_db)):
    user = await get_user(username, db)
    if user is None:
        # Обработка случая, когда пользователь не найден
        # Например, возбуждение исключения или возврат информации об отсутствии пользователя
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    if user is not None and pwd_context.verify(password, user.hashed_password):
        return user



async def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)


async def authenticate_user(username: str, password: str, db: async_session = Depends(get_db)):
    # user = await db.execute(select(User).where(User.fio == username))
    try:
        user = await get_user(username, db)
        verify = await verify_password(password, user.hashed_password)
        if user is None:
            # Обработка случая, когда пользователь не найден
            # Например, возбуждение исключения или возврат информации об отсутствии пользователя
            raise HTTPException(status_code=404, detail="Пользователь не найден.")
        if user and verify:
            return user
        else:
            return "user"
    except:
        return "user"


async def get_current_user_from_cookie(Authorization: str | None = Cookie()):
    try:
        if Authorization != None:
            # Расшифровать токен и выполнить необходимые проверки
            payload = jwt.decode(Authorization, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            # Вернуть информацию о пользователе, если все в порядке
            return {"username": username}
        else:
            return {"username": '0'}

    except Exception as e:
        return {"username": '0'}
#     pass


# # Роут для регистрации пользователя
# @auth_router.post("/register/")
# async def register_user(username: str = Form(), password: str = Form(),
#                         db: async_session = Depends(get_db)):
#     try:
#         username = username
#         hashed_password = pwd_context.hash(password)
#         result = await db.execute(insert(User).values(id=2, fio=username, hashed_password=hashed_password,
#                                                       is_superuser=False, is_verified=False,
#                                                       role=' ', created_at=datetime.now()))
#         await db.commit()
#
#         return result
#     except Exception as e:
#         return {"error": str(e)}


# # Роут для регистрации пользователя
# @auth_router.get("/register/")
# async def register_user(request: Request,
#                         db: async_session = Depends(get_db)):
#     return templates.TemplateResponse("register.html", {"request": request, "msg": "login"})


# Роут для отображения формы входа
@auth_router.get("/login", response_class=HTMLResponse, name="show_login_form")
async def show_login_form(request: Request, msg: str = None):
    try:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "login"})
    except:
        pass

@auth_router.post("/login")
async def login(request: Request, form_data:
OAuth2PasswordRequestForm = Depends(),
                db: async_session = Depends(get_db)):
    try:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Неправильное имя или пароль"})
    except:
        pass


# Роут для генерации токена аутентификации
@auth_router.post("/token")
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: async_session = Depends(get_db)):
    try:
        username = form_data.username
        password = form_data.password
        user = await authenticate_user(username, password, db)
        if user == 'user':
            redirect_url = "/login"
            # redirect_url = request.url_for("show_login_form")
            headers = {
                "Set-Cookie": f"Authorization=a; Path=/; Max-Age=1",
            }
            return RedirectResponse(url=redirect_url, headers=headers)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.fio})

        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Преобразуйте в UTC и форматируйте как строку
        expires_utc = expires.replace(tzinfo=timezone.utc)
        expires_str = expires_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")

        response.set_cookie(
            key="Authorization",
            value=f"{access_token}",
            path="/",
        )
        redirect_url = "/admin/orders/"
        # Добавление куки в хедеры
        headers = {
            "Set-Cookie": f"Authorization={access_token}; Path=/",
        }
        return RedirectResponse(url=redirect_url, headers=headers)
    except Exception as e:
        pass


# Этот эндпоинт будет использоваться для выхода из системы (логаута)
@auth_router.get("/logout")
def logout(response: Response, request: Request):
    try:
        response.delete_cookie("Authorization", path="/")
        redirect_url = "/login"
        # redirect_url = request.url_for("show_login_form")
        headers = {
            "Set-Cookie": f"Authorization=a; Path=/; Max-Age=1",
        }
        return RedirectResponse(url=redirect_url, headers=headers)
    except:
        pass
