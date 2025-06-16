from logging import getLogger
from typing import Literal

from sqlalchemy import select, update
from src.database.core import engine, Session
from src.database.models import Study, User
import json

logger = getLogger(__name__)

async def register_user_object(chat_id: int, encrypted_password: str) -> str:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            current_session.add(User(chat_id=chat_id, state="login"))

async def get_average_score(chat_id: int) -> float:
    with Session(bind=engine) as current_session:
        request = select(Study.objects).where(Study.chat_id == chat_id)
        objects = json.load(current_session.execute(request).scalar())
        average = sum(objects.keys()) / len(objects)
    logger.info(f"Sent average score for {chat_id}")
    return average

async def add_objects(chat_id: int, objects: dict) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            current_session.add(Study(chat_id=chat_id, objects=objects))
    logger.info(f"Objects added for {chat_id}")

async def change_object_score(chat_id: int, object: str, score: float) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = select(Study.objects).where(Study.chat_id == chat_id)
            objects = current_session.execute(request).scalar()
            objects[object] = score
            new_request = update(Study.objects).where(Study.chat_id == chat_id).values(objects=objects)
            current_session.execute(new_request).scalar()
    logger.info(f"Objects score changed for {chat_id}")

async def get_state(chat_id: int) -> str:
    with Session(bind=engine) as current_session:
        request = select(User.state).where(User.chat_id == chat_id)
        return current_session.execute(request).scalar()

async def update_login(chat_id: int, login: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(login_service=login)
            current_session.execute(request)

async def update_password(chat_id: int, password: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(password_service=password)
            current_session.execute(request)

async def update_mode(chat_id: int, mode: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(mode=mode)
            current_session.execute(request)
