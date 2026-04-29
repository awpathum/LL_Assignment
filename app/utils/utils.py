import json


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
    # logging.info(trading_data)
    # trading_data_by_day = trading_data.get("Monthly Time Series", {})

    # print(trading_data_by_day)

    highs = []
    lows = []
    volumes = []

    for data_point in trading_data.values():
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
