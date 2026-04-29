import requests

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


class APIClient:
    def __init__(self):
        import os

        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY environment variable not found")

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
        except requests.Timeout:
            error_msg = f"API request timeout for symbol {symbol}"
            return {"error": error_msg}
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Alpha Vantage API: {str(e)}")

        return response.json()
