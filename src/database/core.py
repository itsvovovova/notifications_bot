from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from logging import getLogger
from src.config import get_settings
from src.database.models import Base

log = getLogger(__name__)

database_url = get_settings().database_url

engine = create_engine(database_url)

Base.metadata.create_all(engine)
Session = sessionmaker(autoflush=False, bind=engine)