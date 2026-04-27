from fastapi import FastAPI, Depends
from db_config import get_db
import logging
import requests

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("TradingSummary")


app = FastAPI()


@app.get("/")
def getYearlyTradingSummary():

    response = process_request()
    return response


def process_request():
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo"
    logger.debug(f"Calling API: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes

        trading_data = response.json()

        summary = calculate_summary(trading_data)
        logger.info(summary)

        return summary

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Alpha Vantage API: {str(e)}")
        return {
            "error": f"Failed to fetch trading data: {str(e)}",
        }


def calculate_summary(trading_data):
    trading_data_by_day = trading_data.get("Monthly Time Series", {})

    # print(trading_data_by_day)

    highs = []
    lows = []
    volumes = []

    for data_point in trading_data_by_day.values():
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
