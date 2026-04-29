from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.logger import logger
from app.models.monthly_trading_data import MonthlyTradingData

load_dotenv()


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
    is_success = False
    try:
        records = api_data.get("Monthly Time Series", {})
        metadata = api_data.get("Meta Data", {})
        symbol = metadata.get("2. Symbol", None)

        with engine.begin() as conn:
            for date, record in records.items():
                open = record.get("1. open", None)
                high = record.get("2. high", None)
                low = record.get("3. low", None)
                close = record.get("4. close", None)
                volume = record.get("5. volume", None)

                if symbol is None or high is None or low is None or volume is None:
                    logger.warning(
                        f"Skipping record for date {date} due to missing required fields"
                    )
                    continue

                conn.execute(
                    text("""
                    INSERT OR REPLACE INTO monthly_data
                    (symbol, date, open, high, low, close, volume)
                    VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
                """),
                    {
                        "symbol": symbol,
                        "date": date,
                        "open": float(open),
                        "high": float(high),
                        "low": float(low),
                        "close": float(close),
                        "volume": int(volume),
                    },
                )
            logger.info("All records inserted successfully")
            conn.commit()
            is_success = True
    except Exception as e:
        logger.error(f"Error writing monthly trade data: {str(e)}")
        raise
    finally:
        return is_success


def get_monthly_data_from_db(symbol, year):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT date, open, high, low, close, volume 
                    FROM monthly_data 
                    WHERE symbol = :symbol AND date LIKE :year_pattern
                    ORDER BY date DESC
                    """
                ),
                {"symbol": symbol, "year_pattern": f"{year}-%"},
            )

            rows = result.fetchall()

            if not rows:
                return None

            # Format data to match API response structure
            monthly_series = {}
            for row in rows:
                date = str(row[0])
                # monthly_series[date] = {
                #     "1. open": str(row[1]) if row[1] is not None else "",
                #     "2. high": str(row[2]) if row[2] is not None else "",
                #     "3. low": str(row[3]) if row[3] is not None else "",
                #     "4. close": str(row[4]) if row[4] is not None else "",
                #     "5. volume": str(row[5]) if row[5] is not None else "",
                # }
                monthly_series[date] = MonthlyTradingData(
                    date=date,
                    open_val=row[1],
                    high=row[2],
                    low=row[3],
                    close=row[4],
                    volume=row[5],
                )

            return monthly_series
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return None
