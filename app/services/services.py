import requests
import json
import os
from pathlib import Path
from app.logger import logger
import jsonschema
from jsonschema import validate

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


class APIClient:
    def __init__(self):
        import os

        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY environment variable not found")

    def read_from_api(self, symbol: str):

        response = self.fetch_data(symbol)
        data = self.validate_api_data(response)
        return data

    def fetch_data(self, symbol: str):

        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")

        params = {
            "function": "TIME_SERIES_MONTHLY",
            "symbol": symbol.upper(),
            "apikey": self.api_key,
        }

        try:
            response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            error_msg = f"API request timeout for symbol {symbol}"
            logger.error(error_msg)
            return {"error": error_msg}
        except requests.ConnectionError as e:
            error_msg = (
                f"Connection error calling Alpha Vantage API for {symbol}: {str(e)}"
            )
            logger.error(error_msg)
            return {"error": error_msg}
        except requests.RequestException as e:
            error_msg = f"Error calling Alpha Vantage API: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def validate_api_data(self, data):
        """Note: We can validate this response using sample_response.json file, without hardcoding field names in the code.
        But for the simplicity, we will validate the response using hardcoded field names.
        We can implement a more robust validation method, but it is out of scope of this assignment.
        """

        if not data:
            return {"error": "No data received from API"}

        if "Error Message" in data:
            return {"error": f"API error: {data['Error Message']}"}

        if "Meta Data" not in data or "2. Symbol" not in data["Meta Data"]:
            return {
                "error": "Unexpected API response format: 'Meta Data' or '2. Symbol' key not found"
            }
        if "Monthly Time Series" not in data:
            return {
                "error": "Unexpected API response format: 'Monthly Time Series' key not found"
            }

        return data
