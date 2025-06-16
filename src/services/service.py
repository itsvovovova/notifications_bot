from logging import getLogger
from src.database.service import get_average_score, register_user_object, update_login, \
    update_password, update_mode
from cryptography.fernet import Fernet
from src.config import get_settings

logger = getLogger(__name__)

fernet = Fernet(get_settings().FERNET_KEY)

async def change_mode(chat_id: int, mode: str) -> str:
    if mode in ["active", "passive"]:
        await update_mode(chat_id, mode)
        return "Mode success updated!"

async def get_score(chat_id: int) -> str:
    average = get_average_score(chat_id)
    return f"Average score: {average}"

async def register_user(chat_id: int, first_name: str) -> str:
    response = "Hello!"
    await register_user_object(chat_id, first_name)
    return response

async def handler_login(chat_id: int, message: str) -> str:
    if message.isdigit() and 10 ** 5 <= int(message) <= 10 ** 6 - 1:
        await update_login(chat_id, message)
        return "Login success added"
    return "Uncorrected login :("

async def handler_password(chat_id: int, message: str) -> str:
    password_encrypted = fernet.encrypt(message.encode())
    """
    Тут нужно попробовать войти на сайт
    """
    await update_password(chat_id, message)







