from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase
from config import DatabaseConfig


engine = create_engine(DatabaseConfig.SQLALCHEMY_DATABASE_URI)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))


class Base(DeclarativeBase):
    pass
