from sqlalchemy_utils.utils import starts_with
from src.database.core import AsyncSessionLocal
from src.database.service import get_state
from src.services.service import register_user, get_score, handler_login, handler_password
from src.create_bot import bot

def middleware_function(function):
    async def wrapper(message):
        async with AsyncSessionLocal() as session:
            current_state = await get_state(message.chat.id, session)
            if current_state == 'login':
                return await handler_login_user(message)
            elif current_state == 'password':
                return await handler_password_user(message)

            if current_state == 'accepted':
                return await function(message)

            text = 'пароль' if current_state == 'password' else 'логин'

            await bot.send_message(message.chat.id, f"Вы не авторизованы, введите {text}")
    return wrapper

async def function_message(message, function, *args):
    async with AsyncSessionLocal() as session:
        response_text = await function(message.chat.id, *args, session)
        await bot.send_message(message.chat.id, response_text)

@bot.message_handler(func=lambda message: message.text and all(not starts_with(message.text, u) for u in ("/score", "/start")))
@middleware_function
async def handler_request(message):
    await bot.send_message(message.chat.id, "Что-что-что ? Я не совсем понял тебя :(")

@bot.message_handler(commands=['start'])
async def handler_start(message):
    await function_message(message, register_user)

@bot.message_handler(commands=['score'])
@middleware_function
async def handler_score(message):
    await function_message(message, get_score)

async def handler_login_user(message):
    await function_message(message, handler_login, message.text)

async def handler_password_user(message):
    await function_message(message, handler_password, message.text)














