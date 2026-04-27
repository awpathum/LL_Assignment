from fastapi import FastAPI
import logging
import requests
from app.services.services import APIClient

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("TradingSummary")


app = FastAPI()


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
    cached_data = check_db(symbol, year)

    if cached_data is None:
        # calling the api
        # api_client = APIClient

        try:
            response = api_client.fetch_data(symbol, year)
            # logging.info(response)

            success = write_to_db()

            # summary = calculate_summary(trading_data)
            # logger.info(summary)

            return calculate_summary(response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Alpha Vantage API: {str(e)}")
            return {
                "error": f"Failed to fetch trading data: {str(e)}",
            }
    else:
        return cached_data


def write_to_db():
    pass


def check_db(symbol, year):
    pass


def calculate_summary(trading_data):
    # logging.info(trading_data)
    trading_data_by_day = trading_data.get("Monthly Time Series", {})

    # print(trading_data_by_day)

    highs = []
    lows = []
    volumes = []

    for data_point in trading_data_by_day.values():
        logging.info(data_point)
        highs.append(float(data_point["2. high"]))
        lows.append(float(data_point["3. low"]))
        volumes.append(int(data_point["5. volume"]))

    logger.info(highs)
    logger.info(lows)
    logger.info(volumes)

    return {
        "highest": max(highs) if highs else 0,
        "lowest": min(lows) if lows else 0,
        "total_volumn": sum(volumes) if volumes else 0,
    }


# https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo
