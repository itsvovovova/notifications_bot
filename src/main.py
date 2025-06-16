from telebot.async_telebot import AsyncTeleBot
from src.config import get_settings
from fastapi import FastAPI
from src.api.telegram_router import lifespan, current_router

app = FastAPI(lifespan=lifespan)

app.include_router(current_router)

bot = AsyncTeleBot(get_settings().bot_token)
bot.infinity_polling()