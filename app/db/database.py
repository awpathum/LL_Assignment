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


def load_db_data_keys():
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""SELECT symbol, date FROM monthly_data"""))
            data_keys = set((row[0], row[1]) for row in result)
            logger.info(f"Loaded {len(data_keys)} data keys from the database")
            return data_keys
    except Exception as e:
        logger.error(f"Error loading data keys from the database: {str(e)}")
        raise


def create_tables():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """CREATE TABLE IF NOT EXISTS monthly_data (
                        symbol TEXT NOT NULL,
                        date TEXT NOT NULL,
                        open REAL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL,
                        volume INTEGER NOT NULL,
                        PRIMARY KEY (symbol, date)
                    )"""
                )
            )
        logger.info("monthly_data table created successfully")
    except Exception as e:
        raise


def write_monthly_trade_data(api_data):
    try:
        records = api_data.get("Monthly Time Series", {})
        metadata = api_data.get("Meta Data", {})
        symbol = metadata.get("2. Symbol", None)

        with engine.begin() as conn:
            for date, record in records.items():
                logger.info(f"Inserting record for date: {date}")
                logger.info(f"Record data: {record}")

                # Extract year, month from date string (format: YYYY-MM-DD)
                date_parts = date.split("-")

                conn.execute(
                    text(
                        """
                    INSERT OR REPLACE INTO monthly_data
                    (symbol, date, open, high, low, close, volume)
                    VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
                """
                    ),
                    {
                        "symbol": symbol,
                        "date": date,
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
