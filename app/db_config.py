from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trade_summary.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
