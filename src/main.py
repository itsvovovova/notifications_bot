from asyncio import run
import src.api.handlers
from src.config import get_settings
from src.create_bot import bot

print("DB URL:", get_settings().database_url)

async def main():
    await bot.infinity_polling()
run(main())