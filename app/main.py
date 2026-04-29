from fastapi import FastAPI
import logging
import requests
from app.services.services import APIClient
from app.db.database import (
    create_tables,
    write_monthly_trade_data,
    load_db_data_keys,
    create_indexes,
    engine,
)
from sqlalchemy import text

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("TradingSummary")


app = FastAPI()


create_tables()
create_indexes()

data_keys = load_db_data_keys()
# logger.debug(f"Initial data keys loaded: {len(data_keys)} entries")


@app.get("/symbols/{symbol}/annual/{year}")
def getYearlyTradingSummary(symbol: str, year: int):
    api_client = APIClient()
    response = process_request(symbol, year, api_client)
    return response


def process_request(
    symbol,
    year,
    api_client: APIClient,
):
    # cached_data = check_db(symbol, year)
    logger.debug(f"Initial data keys loaded: {len(data_keys)} entries")

    if (symbol, year) in data_keys:
        logger.info(f"Data for {symbol} in {year} found in database cache")
        data = get_monthly_data_from_db(symbol, year)
        if data:
            logger.info(
                f"Data for {symbol} in {year} successfully retrieved from database"
            )
        else:
            logger.warning(
                f"Data for {symbol} in {year} was expected in database but not found"
            )
    else:
        logger.info(f"No cached data for {symbol} in {year} found in database")
        data = read_from_api(api_client, symbol, year)
        if data and "error" not in data:
            try:
                write_monthly_trade_data(data)
                data_keys.add((symbol, year))
            except Exception as e:
                logger.error(f"Error writing data to database: {str(e)}")

    logger.debug(f"data_keys updated: {data_keys}")
    return calculate_summary(data)


def read_from_api(api_client: APIClient, symbol: str, year: int):
    try:
        response = api_client.fetch_data(symbol, year)
        return response

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Alpha Vantage API: {str(e)}")
        return {
            "error": f"Failed to fetch trading data: {str(e)}",
        }


def write_to_db():
    pass


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
                date = row[0]
                monthly_series[date] = {
                    "1. open": str(row[1]),
                    "2. high": str(row[2]),
                    "3. low": str(row[3]),
                    "4. close": str(row[4]),
                    "5. volume": str(row[5]),
                }

            return {"Monthly Time Series": monthly_series}
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
        return None


def calculate_summary(trading_data):
    # logging.info(trading_data)
    trading_data_by_day = trading_data.get("Monthly Time Series", {})

    # print(trading_data_by_day)

    highs = []
    lows = []
    volumes = []

    for data_point in trading_data_by_day.values():
        # logging.info(data_point)
        highs.append(float(data_point["2. high"]))
        lows.append(float(data_point["3. low"]))
        volumes.append(int(data_point["5. volume"]))

    # logger.info(highs)
    # logger.info(lows)
    # logger.info(volumes)

    return {
        "highest": max(highs) if highs else 0,
        "lowest": min(lows) if lows else 0,
        "total_volumn": sum(volumes) if volumes else 0,
    }


# https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo
