from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE = {
    'drivername': os.getenv('DB_DRIVER', default='postgresql'),
    'host': os.getenv('DB_HOST', default='localhost'),
    'port': os.getenv('DB_PORT', default='5432'),
    'username': os.getenv('DB_USERNAME', default='postgres'),
    'password': os.getenv('DB_PASSWORD', default='password'),
    'database': os.getenv('DB_NAME', default='jewelry-shop-db')
}

engine = create_engine(URL(**DATABASE))
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()
Base.query = session.query_property()