from fastapi import FastAPI
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("TradingSummary")


app = FastAPI()


@app.get("/")
def getYearlyTradingSummary():
    logger.info("getYearlyTradingSummary")
    return {"high": "80.8700", "low": "76.0600", "volume": "139457800"}
