from logging import getLogger

from sqlalchemy import select, update
from src.database.core import engine, Session
from src.database.models import Study, User
import json

logger = getLogger(__name__)

async def register_user_object(chat_id: int, encrypted_password: str) -> None:
    with Session(bind=engine) as current_session:
        user = current_session.get(User, chat_id)
        if not user:
            current_session.add(User(chat_id=chat_id, state="login"))
            current_session.commit()


async def get_average_score(chat_id: int) -> float:
    with Session(bind=engine) as current_session:
        request = select(Study.objects).where(Study.chat_id == chat_id)
        objects = json.load(current_session.execute(request).scalar())
        average = sum(objects.keys()) / len(objects)
    logger.info(f"Sent average score for {chat_id}")
    return average

async def add_objects(chat_id: int, objects: dict) -> None:
    with Session(bind=engine) as current_session:
        current_session.add(Study(chat_id=chat_id, objects=objects))
        current_session.commit()
    logger.info(f"Objects added for {chat_id}")

async def change_object_score(chat_id: int, object: str, score: float) -> None:
    with Session(bind=engine) as current_session:
        request = select(Study.objects).where(Study.chat_id == chat_id)
        objects = current_session.execute(request).scalar()
        objects[object] = score
        new_request = update(Study.objects).where(Study.chat_id == chat_id).values(objects=objects)
        current_session.execute(new_request).scalar()
        current_session.commit()
    logger.info(f"Objects score changed for {chat_id}")

async def get_state(chat_id: int) -> str:
    with Session(bind=engine) as current_session:
        request = select(User.state).where(User.chat_id == chat_id)
        return current_session.execute(request).scalar()

async def update_login(chat_id: int, login: str) -> None:
    with Session(bind=engine) as current_session:
        request = update(User).where(User.chat_id == chat_id).values(login_service=login)
        current_session.execute(request)
        request = update(User).where(User.chat_id == chat_id).values(state="password")
        current_session.execute(request)
        current_session.commit()

async def update_password(chat_id: int, password: str) -> None:
    with Session(bind=engine) as current_session:
        request = update(User).where(User.chat_id == chat_id).values(password_service=password)
        current_session.execute(request)
        request = update(User).where(User.chat_id == chat_id).values(state="accepted")
        current_session.execute(request)
        current_session.commit()


async def update_mode(chat_id: int, mode: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(mode=mode)
            current_session.execute(request)

async def get_login(chat_id: int) -> str:
    with Session(bind=engine) as current_session:
        request = select(User.login_service).where(User.chat_id == chat_id)
        return current_session.execute(request).scalar()

async def update_state(chat_id: int, state: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(state=state)
            current_session.execute(request)

async def update_php_session(chat_id: int, session: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(php_session=session)
            current_session.execute(request)

async def update_remember_me_session(chat_id: int, session: str) -> None:
    with Session(bind=engine) as current_session:
        with current_session.begin():
            request = update(User).where(User.chat_id == chat_id).values(remember_me_session=session)
            current_session.execute(request)

async def get_remember_me(chat_id: int) -> str:
    with Session(bind=engine) as current_session:
        request = select(User.remember_me_session).where(User.chat_id == chat_id)
        return current_session.execute(request).scalar()