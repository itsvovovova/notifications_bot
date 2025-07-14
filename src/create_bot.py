from telebot.async_telebot import AsyncTeleBot
from src.config import get_settings

bot = AsyncTeleBot(get_settings().BOT_TOKEN)