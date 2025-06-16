from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class Base(DeclarativeBase):
    pass

class Study(Base):
    __tablename__ = "info study"
    chat_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    objects: Mapped[dict] = mapped_column(JSONB)

class User(Base):
    __tablename__ = "users"
    chat_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    login_service: Mapped[str]
    password_service: Mapped[str]
    mode: Mapped[str]
    state: Mapped[str]

class Notification(Base):
    __tablename__ = "notifications"
    chat_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str]

