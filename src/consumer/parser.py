import asyncio
import json

import aiohttp
from aio_pika import connect_robust
from fastapi import HTTPException

from src.config import get_settings
from logging import getLogger

from src.database.core import AsyncSessionLocal
from src.database.service import get_login, get_remember_me, get_objects, update_objects, get_all_users
from src.create_bot import bot

logger = getLogger(__name__)


async def parse_data(chat_id: int) -> dict:
        async with AsyncSessionLocal() as session:
            remember_me = await get_remember_me(chat_id, session)
            login = await get_login(chat_id, session)

            url = "https://lk.gubkin.ru/new/api/api.php"
            params = {
                "module": "study",
                "resource": "Performance",
                "method": "getPerformance",
                "studentId": f'{login}-1'
            }
            cookies = {"remember_me": remember_me}
            headers = {"User-Agent": "Mozilla/5.0"}

            async with aiohttp.ClientSession() as http_session:
                async with http_session.get(url, params=params, cookies=cookies, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    raise HTTPException(status_code=404, detail="Not found")


async def check_updates(chat_id: int, new_data: dict) -> dict:
    update_dict = {}
    async with AsyncSessionLocal() as session:
        last_data = await get_objects(chat_id, session)
    for object_name in new_data:
        if object_name in last_data and new_data[object_name] != last_data[object_name]:
            update_dict[object_name] = (last_data[object_name], new_data[object_name])
    return update_dict


async def process_user(chat_id: int):
    # Парсим данные
    new_data = await parse_data(chat_id)

    # Проверяем обновления
    if await check_updates(chat_id, new_data):
        # Сохраняем новые данные
        async with AsyncSessionLocal() as session:
            objects = await get_objects(chat_id, session)
            updated_objects = await check_updates(chat_id, new_data)
            for object_name in updated_objects:
                objects[object_name] = updated_objects[object_name][1]
            await update_objects(chat_id, objects, session)


        # Отправляем уведомление
        for object_name in updated_objects:
            flag = "+" if updated_objects[object_name][1] - updated_objects[object_name][0] > 0 else ""
            await bot.send_message(chat_id=chat_id, text=f"🔄 [{object_name}]: {updated_objects[object_name][0]} -> {updated_objects[object_name][1]} [{flag}{updated_objects}]")
        logger.info(f"Отправлено уведомление для {chat_id}")


async def main_worker():
    settings = get_settings()

    while True:
        try:
            # Подключаемся к RabbitMQ
            connection = await connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_user,
                password=settings.rabbitmq_password,
            )

            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue('gubkin_parser_queue', durable=True)
                logger.info("Парсер подключен к RabbitMQ")

                # Обрабатываем сообщения
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            data = json.loads(message.body.decode())
                            await process_user(data['chat_id'])

        except Exception as e:
            logger.error(f"Ошибка подключения: {str(e)}")
            await asyncio.sleep(10)  # Переподключение через 10 сек


async def periodic_parser():
    while True:
        async with AsyncSessionLocal() as session:
            active_users = await get_all_users(session)
            for user in active_users:
                await process_user(user)
            await asyncio.sleep(30)

async def main():
    await asyncio.gather(
        main_worker(),
        periodic_parser()
    )
asyncio.run(main())