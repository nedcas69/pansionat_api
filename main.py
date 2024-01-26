import logging

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from typing import Union

from orders_api import orderApi_router
from auth import auth_router
from order import order_router

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
# Создаем файловый обработчик и указываем путь к файлу
file_handler = logging.FileHandler("app_log_file.log")
# Создаем форматтер для логов
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
# Получаем корневой логгер и добавляем к нему файловый обработчик
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
# Устанавливаем уровень логирования для корневого логгера
root_logger.setLevel(logging.DEBUG)


# Обработчик для записи логов при возникновении ошибок
def error_handler(request: Request, exc: Union[HTTPException, RequestValidationError, Exception]):
    logger = logging.getLogger(__name__)
    logger.exception("Error processing request")
    return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# Добавляем обработчик ошибок к FastAPI
app.add_exception_handler(HTTPException, error_handler)
app.add_exception_handler(RequestValidationError, error_handler)


@app.get('/')
async def main():
    return RedirectResponse(url="/admin/orders/1")

try:
    # Включаем роутеры в блоке try
    app.include_router(orderApi_router)
    app.include_router(auth_router)
    app.include_router(order_router)
except Exception as e:
    # Обрабатываем и логируем исключение, если оно произошло при включении роутеров
    logger = logging.getLogger(__name__)
    logger.exception(f"Произошла ошибка при включении маршрутизаторов: {e}")

