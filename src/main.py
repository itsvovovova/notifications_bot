from asyncio import run
import src.api.handlers
from src.database.core import create_tables
from src.create_bot import bot


async def main():
    await create_tables()
    await bot.infinity_polling()

if __name__ == "__main__":
    run(main())