import requests

ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"


class APIClient:
    def __init__(self):
        import os

        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY environment variable not found")

    def fetch_data(self, symbol: str, year: int):
        params = {
            "function": "TIME_SERIES_MONTHLY",
            "symbol": symbol.upper(),
            "apikey": self.api_key,
        }

        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params, timeout=10)

        return response.json()
