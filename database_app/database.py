from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///./db_app.db'

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False},  # only for sqlite
)
# for creating db session instances (the Session class will be needed too later)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base class for all orm table models
Base = declarative_base()
