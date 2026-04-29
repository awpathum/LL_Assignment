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
            result = conn.execute(
                text(
                    """SELECT DISTINCT symbol, CAST(SUBSTR(date, 1, 4) AS INTEGER) as year 
                                           FROM monthly_data 
                                           ORDER BY symbol, year DESC"""
                )
            )
            data_keys = set((row[0], row[1]) for row in result)
            logger.info(f"Loaded {len(data_keys)} data keys from the database")
            logger.debug(f"Data keys: {data_keys}")
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


def create_indexes():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_symbol_date ON monthly_data(symbol, date)"
                )
            )
        logger.info("Indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        raise


def write_monthly_trade_data(api_data):
    try:
        records = api_data.get("Monthly Time Series", {})
        metadata = api_data.get("Meta Data", {})
        symbol = metadata.get("2. Symbol", None)

        with engine.begin() as conn:
            for date, record in records.items():

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
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error writing monthly trade data: {str(e)}")
        raise
