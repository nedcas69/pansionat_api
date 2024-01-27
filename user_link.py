import json
from sched import scheduler
import requests
from requests.auth import HTTPBasicAuth
from aiogram.types import Message, ChatJoinRequest, ContentType
from data import config
from data.config import C_USER, C_PASS, C_URI
from filters import IsGroup, IsAdmin, IsPrivate
from loader import dp, bot


@dp.message_handler(content_types = ['new_chat_members', 'left_chat_member']) # удаляет " покинул(а) в группу"
async def delete(message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Ошибка при добавлении пользователя в группу: {e}")

users = []


@dp.message_handler(IsGroup(), text='mess_id') # Создаём message handler который ловит команду /menu
async def menu(message: Message): # Создаём асинхронную функцию
    # Отправляем сообщение пользователю
    await message.answer(message)


@dp.message_handler(IsPrivate(), content_types=ContentType.CONTACT)
async def contct(message: Message):
    try:
        text = message.contact.phone_number
        contact = message.contact.user_id
        user_id = message.from_user.id
        group_chat_id = '-1001855063926'
        # await bot.add_chat_member(chat_id=group_chat_id, user_id=contact)
        index_to_remove = 0  # Индекс элемента, который вы хотите удалить

        new_text = text[:index_to_remove] + text[index_to_remove + 1:]
        auth = HTTPBasicAuth(C_USER, C_PASS)
        r = requests.get(C_URI + new_text, auth=auth)
        html = r.text.encode('ISO-8859-1').decode('utf-8-sig')
        if html == '':
            auth = HTTPBasicAuth(C_USER, C_PASS)
            r = requests.get(C_URI + text, auth=auth)
            html = r.text.encode('ISO-8859-1').decode('utf-8-sig')

        if html != '':
            users.append(user_id)
            await message.answer('Тех-поддержкани группаси https://t.me/+kIfIurLPn44wZjAy')
        print(user_id)

        print(users)
        print(html)
    except Exception as e:
        print(f"Ошибка при добавлении пользователя в группу: {e}")


@dp.chat_join_request_handler()
async def some_handler(cally: ChatJoinRequest):
    chats = -1001855063926
    user = cally.from_user.id
    print(type(cally))

    if user in users:
        await cally.approve()

