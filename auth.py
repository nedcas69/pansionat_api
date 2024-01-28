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
    return None


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
            # Просто выведите токен для отладки
            print("Received token:", Authorization)
            # Расшифровать токен и выполнить необходимые проверки
            payload = jwt.decode(Authorization, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            # if not username:
            #     redirect_url = '/login'
            #     return RedirectResponse(url=redirect_url)
            print(Authorization, '\n', username)
            # Вернуть информацию о пользователе, если все в порядке
            return {"username": username}
        else:
            return {"username": '0'}

    except Exception as e:
        # redirect_url = "/login"
        # return RedirectResponse(url=redirect_url)
        print(str(e))
        return {"username": '0'}
#     pass


# Роут для регистрации пользователя
@auth_router.post("/register/")
async def register_user(username: str, password: str,
                        db: async_session = Depends(get_db)):
    try:
        username = username
        hashed_password = pwd_context.hash(password)
        result = await db.execute(insert(User).values(id=1, fio=username, hashed_password=hashed_password,
                                                      is_superuser=False, is_verified=False,
                                                      role=' ', created_at=datetime.now()))
        await db.commit()

        return result
    except Exception as e:
        return {"error": str(e)}


# Роут для отображения формы входа
@auth_router.get("/login", response_class=HTMLResponse, name="show_login_form")
async def show_login_form(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "msg": "login"})

@auth_router.post("/login")
async def login(request: Request, form_data:
OAuth2PasswordRequestForm = Depends(),
                db: async_session = Depends(get_db)):
    return templates.TemplateResponse("login.html", {"request": request, "msg": "Неправильное имя или пароль"})


# Роут для генерации токена аутентификации
@auth_router.post("/token")
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: async_session = Depends(get_db)):
    # try:
    #     username = form_data.get("username")
    #     password = form_data.get("password")
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
    access_token = create_access_token(data={"sub": user.fio}, expires_delta=access_token_expires)
    print(user.fio, access_token)

    # response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    # response = {"access_token": access_token}
    # response.set_cookie("Authorization", f"Bearer {access_token}", httponly=True, path="/")

    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Преобразуйте в UTC и форматируйте как строку
    expires_utc = expires.replace(tzinfo=timezone.utc)
    expires_str = expires_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Вычисляем дату и время истечения срока действия токена
    # expiration_time = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Устанавливаем куку в HTTP-ответе
    response.set_cookie(
        key="Authorization",
        value=f"{access_token}",
        expires=expires_str,
        path="/",
        # secure=False,  # Установите в True, если ваш сайт работает по HTTPS
        # httponly=True,  # Установите в True, чтобы кука была доступна только через HTTP
    )
    print(response)
    # return response
    redirect_url = "/admin/orders/"
    # Добавление куки в хедеры
    headers = {
        "Set-Cookie": f"Authorization={access_token}; Path=/; Max-Age=3600",
    }
    return RedirectResponse(url=redirect_url, headers=headers)


# except Exception as e:
#     print(str(e))


# Этот эндпоинт будет использоваться для выхода из системы (логаута)
@auth_router.get("/logout")
def logout(response: Response, request: Request):
    response.delete_cookie("Authorization", path="/")
    redirect_url = "/login"
    # redirect_url = request.url_for("show_login_form")
    headers = {
        "Set-Cookie": f"Authorization=a; Path=/; Max-Age=1",
    }
    return RedirectResponse(url=redirect_url, headers=headers)


@auth_router.get("/status", response_model=dict)
async def status(current_user: dict = Depends(get_current_user_from_cookie), ):
    return {"status": "OK", "user": current_user}
