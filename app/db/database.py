from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from app.logger import logger
from app.models.monthly_trading_data import MonthlyTradingData
from app.utils.utils import parse_and_validate_data_point
from app.db.queries import (
    LOAD_DATA_KEYS,
    CREATE_MONTHLY_DATA_TABLE,
    CREATE_SYMBOL_DATE_INDEX,
    INSERT_MONTHLY_DATA,
    GET_MONTHLY_DATA_BY_SYMBOL_YEAR,
)

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
            result = conn.execute(text(LOAD_DATA_KEYS))
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
            conn.execute(text(CREATE_MONTHLY_DATA_TABLE))
        logger.info("monthly_data table created successfully")
    except Exception as e:
        logger.error(f"Error loading data keys from the database: {str(e)}")
        raise


def create_indexes():
    try:
        with engine.begin() as conn:
            conn.execute(text(CREATE_SYMBOL_DATE_INDEX))
        logger.info("Indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        raise


def write_monthly_trade_data(api_data):
    is_success = False
    try:
        data_points = api_data.get("Monthly Time Series", {})
        metadata = api_data.get("Meta Data", {})
        symbol = metadata.get("2. Symbol", None)

        with engine.begin() as conn:
            for date, data_point in data_points.items():
                data_point = parse_and_validate_data_point(data_point)
                if data_point is None:
                    logger.warning(
                        f"Skipping record for date {date} due to validation failure"
                    )
                    continue

                conn.execute(
                    text(INSERT_MONTHLY_DATA),
                    {
                        "symbol": symbol,
                        "date": date,
                        "open": data_point["open"],
                        "high": data_point["high"],
                        "low": data_point["low"],
                        "close": data_point["close"],
                        "volume": data_point["volume"],
                    },
                )
            if data_points:
                logger.info(f"Inserted/updated {len(data_points)} records successfully")
                is_success = True
            else:
                logger.warning("No records found in API response to write")
                is_success = False
    except Exception as e:
        logger.error(f"Error writing monthly trade data: {str(e)}")
        raise
    finally:
        return is_success


def get_monthly_data_from_db(symbol, year):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(GET_MONTHLY_DATA_BY_SYMBOL_YEAR),
                {"symbol": symbol, "year_pattern": f"{year}-%"},
            )

            rows = result.fetchall()

            if not rows:
                return None

            # Format data to match API response structure
            monthly_series = {}
            for row in rows:
                date = str(row[0])
                monthly_series[date] = MonthlyTradingData(
                    date=date,
                    open_val=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[5]),
                )

            return monthly_series
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return None
