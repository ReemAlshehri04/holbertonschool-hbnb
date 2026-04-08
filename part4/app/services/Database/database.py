from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = "sqlite:///hbnb_task8.db"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)
get_session = scoped_session(SessionLocal)
