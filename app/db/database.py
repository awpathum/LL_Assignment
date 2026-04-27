from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("TradingSummary")


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trade_data.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_connection():
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()


def create_tables():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """CREATE TABLE IF NOT EXISTS monthly_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        year TEXT NOT NULL,
                        month TEXT NOT NULL,
                        day TEXT NOT NULL,
                        open REAL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL,
                        volume INTEGER NOT NULL,
                        UNIQUE(date)
                    )"""
                )
            )
        logger.info("monthly_data table created successfully")
    except Exception as e:
        raise


def write_monthly_trade_data(records):
    try:
        with engine.begin() as conn:
            for date, record in records.items():
                logger.info(f"Inserting record for date: {date}")
                logger.info(f"Record data: {record}")

                # Extract year, month from date string (format: YYYY-MM-DD)
                date_parts = date.split("-")
                year = int(date_parts[0])
                month = int(date_parts[1])
                day = int(date_parts[2])

                conn.execute(
                    text(
                        """
                    INSERT OR REPLACE INTO monthly_data
                    (year, month, day, open, high, low, close, volume)
                    VALUES (:year, :month, :date, :open, :high, :low, :close, :volume)
                """
                    ),
                    {
                        "year": year,
                        "month": month,
                        "day": day,
                        "open": float(record.get("1. open")),
                        "high": float(record["2. high"]),
                        "low": float(record["3. low"]),
                        "close": float(record.get("4. close")),
                        "volume": int(record["5. volume"]),
                    },
                )
            logger.info("All records inserted successfully")
            return True
    except Exception as e:
        logger.error(f"Error writing monthly trade data: {str(e)}")
        raise
