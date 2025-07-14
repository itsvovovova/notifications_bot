from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class Base(DeclarativeBase):
    pass

class Study(Base):
    __tablename__ = "info_study"
    chat_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    objects: Mapped[dict] = mapped_column(JSONB)

class User(Base):
    __tablename__ = "users"
    chat_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    login_service: Mapped[str] = mapped_column(nullable=True)
    password_service: Mapped[str] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=True)
    php_session: Mapped[str] = mapped_column(nullable=True)
    remember_me_session: Mapped[str] = mapped_column(nullable=True)

