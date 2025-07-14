from logging import getLogger

import requests

from src.database.service import get_average_score, register_user_object, update_login, \
    update_password, update_mode, get_login, update_state, update_php_session, update_remember_me_session, add_objects, \
    get_remember_me
from cryptography.fernet import Fernet
from src.config import get_settings

logger = getLogger(__name__)

fernet = Fernet(get_settings().FERNET_KEY)

async def change_mode(chat_id: int, mode: str, session) -> str:
    if mode in ["active", "passive"]:
        await update_mode(chat_id, mode, session)
        return "Режим успешно изменен!"

async def get_score(chat_id: int, session) -> str:
    average = await get_average_score(chat_id, session)
    return f"Average score: {average}"

async def register_user(chat_id: int, session) -> str:
    response = ("Привет! У меня доступно несколько команд:\n"
                "/mode - смена режима\n/score - получение среднего результата из ЛК\nЖду твоего сообщения :)")
    await register_user_object(chat_id, session)
    return response

async def handler_login(chat_id: int, message: str, session) -> str:
    if message.isdigit() and 10 ** 5 <= int(message) <= 10 ** 6 - 1:
        await update_login(chat_id, message, session)
        return "Отлично, жду теперь пароль :)"
    return "Некорректный логин, попробуй ввести еще раз"

async def handler_password(chat_id: int, message, current_session):
    login = await get_login(chat_id, current_session)
    password = message
    # Попытка войти на сайт
    login_url = 'https://lk.gubkin.ru/new/api/api.php?module=auth&method=login'
    user = {
        "login": login,
        "password": password,
        "rememberMe": 1
    }
    session = requests.Session()
    response = session.post(login_url, json=user, verify='src/cacert.pem')
    print(response.text)
    if response.status_code != 200:
        await update_state(chat_id, 'login', current_session)
        print(response.text)
        return "Попробуйте еще раз :("
    cookies = session.cookies.get_dict()
    php_session = cookies.get('PHPSESSID')
    remember_me = cookies.get('remember_me')
    await update_php_session(chat_id, php_session, current_session)
    await update_remember_me_session(chat_id, remember_me, current_session)
    await update_password(chat_id, message, current_session)
    objects_response = await parse_objects(chat_id, current_session)
    if objects_response: await add_objects(chat_id, objects_response, current_session)
    return "Получилось! Теперь можешь дергать мои ручки :)"

async def parse_objects(chat_id: int, session):
    remember_me = await get_remember_me(chat_id, session)
    login = await get_login(chat_id, session)
    url = "https://lk.gubkin.ru/new/api/api.php"
    params = {
        "module": "study",
        "resource": "Performance",
        "method": "getPerformance",
        "studentId": f'{login}-1'
    }
    cookies = {
        "remember_me": remember_me
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, params=params, cookies=cookies, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка: {response.status_code}, Ответ: {response.text}")
        return None








