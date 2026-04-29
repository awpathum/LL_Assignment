import json
from app.logger import logger
from app.models.monthly_trading_data import MonthlyTradingData

def get_unique_years(api_response):
    """
    Extracts unique years from a dictionary or JSON string where keys are 'YYYY-MM-DD'.
    """
    # Parse JSON if the input is a string
    if isinstance(api_response, str):
        data = json.loads(api_response)
    else:
        data = api_response

    # Return as a sorted list
    return {date.split("-")[0] for date in data.keys()}


def get_metadata_from_api_response(api_response):
    """
    Extracts metadata from a dictionary or JSON string.
    """
    # Parse JSON if the input is a string
    if isinstance(api_response, str):
        data = json.loads(api_response)
    else:
        data = api_response

    # Extract metadata
    metadata = data.get("Meta Data", {})
    return metadata


def get_monthly_time_series_from_api_response(api_response):
    """
    Extracts the 'Monthly Time Series' data from a dictionary or JSON string.
    """
    # Parse JSON if the input is a string
    if isinstance(api_response, str):
        data = json.loads(api_response)
    else:
        data = api_response

    # Extract monthly time series data
    monthly_time_series = data.get("Monthly Time Series", {})
    return monthly_time_series


def filter_monthly_data_by_year(monthly_time_series, year):
    """
    Filters the monthly time series data to include only entries from the specified year.
    """
    filtered_data = {
        date: record
        for date, record in monthly_time_series.items()
        if date.startswith(str(year))
    }
    return filtered_data


def calculate_summary(monthly_trading_data: dict[str, MonthlyTradingData]):
    if monthly_trading_data is None or not monthly_trading_data:
        logger.warning("No trading data available to calculate summary")
        return {"highest": 0, "lowest": 0, "total_volumn": 0}

    highs = []
    lows = []
    volumes = []

    for date, data_point in monthly_trading_data.items():
        try:
            if not isinstance(data_point, MonthlyTradingData):
                logger.warning(
                    f"Skipping invalid data point for date {date}: not a MonthlyTradingData instance"
                )
                continue

            # Check required fields exist
            high = data_point.high
            low = data_point.low
            volume = data_point.volume

            if high is None or low is None or volume is None:
                logger.warning(f"Skipping date {date}: missing required fields")
                continue

            highs.append(float(high))
            lows.append(float(low))
            volumes.append(int(volume))

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping date {date} due to data parsing error: {str(e)}")
            continue

    if not highs or not lows or not volumes:
        logger.warning("No valid data points found to calculate summary")

    return {
        "highest": max(highs) if highs else 0,
        "lowest": min(lows) if lows else 0,
        "volume": sum(volumes) if volumes else 0,
    }


def parse_and_validate_data_point(data_point):
    """
    we can implemtn a better validation method using 3rd party libraries like jsonschema or pydantic,
    but for the simplicity, we will validate the data point using hardcoded field names and types.
    """
    try:
        if not isinstance(data_point, dict):
            logger.warning("Data point is not a dictionary")
            return None

        required_keys = ["1. open", "2. high", "3. low", "4. close", "5. volume"]
        for key in required_keys:
            if key not in data_point:
                logger.warning(f"Missing required key: {key}")
                return None

        open_val = float(data_point["1. open"])
        high_val = float(data_point["2. high"])
        low_val = float(data_point["3. low"])
        close_val = float(data_point["4. close"])
        volume_val = int(data_point["5. volume"])

        return {
            "open": open_val,
            "high": high_val,
            "low": low_val,
            "close": close_val,
            "volume": volume_val,
        }
    except (ValueError, TypeError) as e:
        logger.warning(f"Data parsing error: {str(e)}")
        return None
