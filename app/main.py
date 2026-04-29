from fastapi import FastAPI
from app.logger import logger
from app.services.services import APIClient
from app.utils.utils import (
    get_unique_years,
    get_monthly_time_series_from_api_response,
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


app = FastAPI()


create_tables()
create_indexes()

data_keys = load_db_data_keys()

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
            """Note: This will write same data set again and again for each year, but it simplifies the logic.

            Suppose we are requsting summary for year 1800. It's not found in the database, so we fetch data from API.
            The API will return data for all years and write the same data to the database. (INSERT OR REPLACE INTO) has used in database.

            We can read min, max years in the database or each symbol and skip the request not with in the range.
            But if there are any updated data in the API, we will miss those if we do not call the API.
            We can implemets a method to run on at timer to sync the database with the API, but it is out of scope of this assignment.

            For the simplicity, we will call the API for each request if the data is not found in the database. It will also ensure that we have the latest data in the database.
            But in a production environment, we should implement a more efficient way to sync the database with the API and avoid unnecessary API calls.
            """

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
    else:
        logger.info(f"Cached data for {symbol} in {year} found in database")

    monthly_series_data = get_monthly_data_from_db(symbol, year)

    return calculate_summary(monthly_series_data)


# https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo
