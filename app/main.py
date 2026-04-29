from fastapi import FastAPI
import logging
import requests
from app.services.services import APIClient
from app.utils.utils import (
    get_unique_years,
    get_metadata_from_api_response,
    get_monthly_time_series_from_api_response,
    filter_monthly_data_by_year,
    calculate_summary,
)
from app.db.database import (
    create_tables,
    write_monthly_trade_data,
    load_db_data_keys,
    create_indexes,
    get_monthly_data_from_db,
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

    if (symbol, year) not in data_keys:

        logger.info(f"No cached data for {symbol} in {year} found in database")
        # data = read_from_api(api_client, symbol, year)
        data = api_client.fetch_data(symbol)
        if not data or "error" in data:
            error_msg = data.get("error", "Unknown error occurred while fetching data")
            logger.error(f"Error fetching data for {symbol}: {error_msg}")
            return {"error": error_msg}

        try:
            write_monthly_trade_data(data)
            unique_years = get_unique_years(
                get_monthly_time_series_from_api_response(data)
            )
            # Add all (symbol, year) combinations to data_keys
            for year_from_api in unique_years:
                data_keys.add((symbol, int(year_from_api)))
            logger.info(f"Added {len(unique_years)} year(s) for {symbol} to data_keys")
        except Exception as e:
            logger.error(f"Error writing data to database: {str(e)}")

    monthly_series_data = get_monthly_data_from_db(symbol, year)

    return calculate_summary(monthly_series_data)


# https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo
