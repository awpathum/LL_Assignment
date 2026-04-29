import json
from app.logger import logger

def get_unique_years(api_response):
    """
    Extracts unique years from a dictionary or JSON string where keys are 'YYYY-MM-DD'.
    """
    # Parse JSON if the input is a string
    if isinstance(api_response, str):
        data = json.loads(api_response)
    else:
        data = api_response

    # Use a set comprehension to extract the first 4 characters of each key
    unique_years = {date.split("-")[0] for date in data.keys()}

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


def calculate_summary(trading_data):
    if trading_data is None or not trading_data:
        logger.warning("No trading data available to calculate summary")
        return {"highest": 0, "lowest": 0, "total_volumn": 0}

    highs = []
    lows = []
    volumes = []

    for date, data_point in trading_data.items():
        try:
            if not isinstance(data_point, dict):
                logger.warning(
                    f"Skipping invalid data point for date {date}: not a dictionary"
                )
                continue

                # Check required keys exist
            if (
                "2. high" not in data_point
                or "3. low" not in data_point
                or "5. volume" not in data_point
            ):
                logger.warning(f"Skipping date {date}: missing required keys")
                continue

            highs.append(float(data_point["2. high"]))
            lows.append(float(data_point["3. low"]))
            volumes.append(int(data_point["5. volume"]))
        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping date {date} due to data parsing error: {str(e)}")
            continue

    return {
        "highest": max(highs) if highs else 0,
        "lowest": min(lows) if lows else 0,
        "total_volumn": sum(volumes) if volumes else 0,
    }
