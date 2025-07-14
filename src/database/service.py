from logging import getLogger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database.models import Study, User
from src.services.fernet_crypt import encrypt_string, decrypt_string

logger = getLogger(__name__)

async def register_user_object(chat_id: int, current_session: AsyncSession) -> None:
    user = await current_session.get(User, chat_id)
    if not user:
        current_session.add(User(chat_id=chat_id, state="login"))
        await current_session.commit()


async def get_average_score(chat_id: int, current_session: AsyncSession) -> float:
    request = select(Study.objects).where(Study.chat_id == chat_id)
    result = await current_session.execute(request)
    objects = result.scalar()
    average = sum(float(x[0]) for x in objects.values()) / len(objects)
    logger.info(f"Sent average score for {chat_id}")
    return average

async def get_objects(chat_id: int, current_session: AsyncSession) -> dict:
    request = select(Study.objects).where(Study.chat_id == chat_id)
    result = await current_session.execute(request)
    objects = result.scalar()
    return objects

async def add_objects(chat_id: int, objects: dict, current_session: AsyncSession) -> None:
    objects_dict = convert_to_dict(objects)
    current_session.add(Study(chat_id=chat_id, objects=objects_dict))
    await current_session.commit()
    logger.info(f"Objects added for {chat_id}")

async def update_objects(chat_id: int, objects: dict, current_session: AsyncSession) -> None:
    objects_dict = convert_to_dict(objects)
    await current_session.execute(
        update(Study)
        .where(Study.chat_id == chat_id)
        .values(objects=objects_dict)
    )
    await current_session.commit()

async def get_state(chat_id: int, current_session: AsyncSession) -> str:
    request = select(User.state).where(User.chat_id == chat_id)
    result = await current_session.execute(request)
    return result.scalar()

async def update_login(chat_id: int, login: str, current_session: AsyncSession) -> None:
    await current_session.execute(
        update(User)
        .where(User.chat_id == chat_id)
        .values(login_service=login, state="password")
    )
    await current_session.commit()


async def update_password(chat_id: int, password: str, current_session: AsyncSession) -> None:
    encrypted_password = encrypt_string(password, get_settings().FERNET_KEY)
    await current_session.execute(
        update(User)
        .where(User.chat_id == chat_id)
        .values(password_service=encrypted_password, state="accepted")
    )
    await current_session.commit()


async def update_mode(chat_id: int, mode: str, current_session: AsyncSession) -> None:
    await current_session.execute(
        update(User)
        .where(User.chat_id == chat_id)
        .values(mode=mode)
    )
    await current_session.commit()


async def get_login(chat_id: int, current_session: AsyncSession) -> str:
    request = select(User.login_service).where(User.chat_id == chat_id)
    result = await current_session.execute(request)
    return result.scalar()


async def update_state(chat_id: int, state: str, current_session: AsyncSession) -> None:
    await current_session.execute(
        update(User)
        .where(User.chat_id == chat_id)
        .values(state=state)
    )
    await current_session.commit()


async def update_php_session(chat_id: int, session: str, current_session: AsyncSession) -> None:
    encrypted_session = encrypt_string(session, get_settings().FERNET_KEY)
    await current_session.execute(
        update(User)
        .where(User.chat_id == chat_id)
        .values(php_session=encrypted_session)
    )
    await current_session.commit()


async def update_remember_me_session(chat_id: int, session: str, current_session: AsyncSession) -> None:
    encrypted_session = encrypt_string(session, get_settings().FERNET_KEY)
    await current_session.execute(
        update(User)
        .where(User.chat_id == chat_id)
        .values(remember_me_session=encrypted_session)
    )
    await current_session.commit()


async def get_remember_me(chat_id: int, current_session: AsyncSession) -> str:
    request = select(User.remember_me_session).where(User.chat_id == chat_id)
    result = await current_session.execute(request)
    return decrypt_string(result.scalar(), get_settings().FERNET_KEY)

def convert_to_dict(data: dict) -> dict:
    subject_scores = {}
    for subject in data['result']['performance']:
        name, max_score = subject['name'], subject['maxPoints']
        current_score = subject['currentPoints']
        subject_scores[name] = (current_score, max_score)
    return subject_scores

async def get_all_users(current_session: AsyncSession):
    request = select(User.chat_id)
    result = await current_session.execute(request)
    return result.scalars().all()