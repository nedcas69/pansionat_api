import datetime
import logging

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from orders_api import orderApi_router
from auth import auth_router
from order import order_router
from rooms import room_router

app = FastAPI()
# Добавляем маршрут для обработки статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Позволяет запросы с любого источника (замените '*' на URL вашего фронтенда в продакшене)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В реальном приложении лучше установить конкретный URL фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
file_name = datetime.date.today()
# Создаем файловый обработчик и указываем путь к файлу
file_handler = logging.FileHandler(f"loc/{file_name}.log", encoding='utf-8')
# Создаем форматтер для логов
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(formatter)
# Получаем корневой логгер и добавляем к нему файловый обработчик
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
# Устанавливаем уровень логирования для корневого логгера
root_logger.setLevel(logging.DEBUG)


@app.get('/')
async def main():
    return RedirectResponse(url="/admin/orders/1")

app.include_router(orderApi_router)
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(room_router)
