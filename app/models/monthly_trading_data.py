class MonthlyTradingData:
    """Represents a single month's trading data point"""

    def __init__(self, date, open_val, high, low, close, volume):
        self.date = date
        self.open = open_val
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def to_dict(self):
        """Convert to API response format dictionary"""
        return {
            "1. open": str(self.open) if self.open is not None else "",
            "2. high": str(self.high) if self.high is not None else "",
            "3. low": str(self.low) if self.low is not None else "",
            "4. close": str(self.close) if self.close is not None else "",
            "5. volume": str(self.volume) if self.volume is not None else "",
        }
