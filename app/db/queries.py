"""
SQL queries for monthly trading data database operations.
"""

# Load distinct symbols and years from the database
LOAD_DATA_KEYS = """
    SELECT DISTINCT symbol, CAST(SUBSTR(date, 1, 4) AS INTEGER) as year 
    FROM monthly_data 
    ORDER BY symbol, year DESC
"""

# Create monthly_data table
CREATE_MONTHLY_DATA_TABLE = """
    CREATE TABLE IF NOT EXISTS monthly_data (
        symbol TEXT NOT NULL,
        date TEXT NOT NULL,
        open REAL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL,
        volume INTEGER NOT NULL,
        PRIMARY KEY (symbol, date)
    )
"""

# Create index on symbol and date
CREATE_SYMBOL_DATE_INDEX = """
    CREATE INDEX IF NOT EXISTS idx_symbol_date ON monthly_data(symbol, date)
"""

# Insert or replace monthly trading data
INSERT_MONTHLY_DATA = """
    INSERT OR REPLACE INTO monthly_data
    (symbol, date, open, high, low, close, volume)
    VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
"""

# Get monthly data for specific symbol and year
GET_MONTHLY_DATA_BY_SYMBOL_YEAR = """
    SELECT date, open, high, low, close, volume 
    FROM monthly_data 
    WHERE symbol = :symbol AND date LIKE :year_pattern
    ORDER BY date DESC
"""
