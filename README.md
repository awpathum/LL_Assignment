# Trading Summary API

A FastAPI-based backend service that fetches and aggregates monthly trading data for stock symbols. This application provides a REST API endpoint to retrieve yearly trading summaries including highest price, lowest price, and total trading volume.

request : GET /symbols/IBM/annual/2005

returns:
{
"high": "80.8700",
"low": "76.0600",
"volume": "139457800"
}

## Features

- **REST API Endpoint** - Get yearly trading summaries for any stock symbol
- **Database Caching** - Efficient SQLite database to cache API responses and avoid redundant API calls
- **Alpha Vantage Integration** - Fetches real-time stock market data from Alpha Vantage
- **Error Handling** - Comprehensive error handling for network issues, API failures, and invalid data
- **Logging** - Detailed logging for debugging and monitoring
- **Index Optimization** - Database indexes for fast query performance

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database ORM**: SQLAlchemy 2.0.23
- **HTTP Client**: Requests 2.31.0
- **Environment Management**: python-dotenv 1.0.0
- **Python**: 3.8+

## Dependencies & Rationale

### Core Framework

- **FastAPI (0.104.1)** - Modern Python web framework for building APIs
  - Automatic interactive API documentation (Swagger UI)
  - Fast performance and native async/await support
  - Type hints and validation built-in
  - Excellent error handling and status codes

- **Uvicorn (0.24.0)** - ASGI web server for running FastAPI
  - Lightweight and production-ready
  - Supports concurrent requests efficiently
  - Better performance than traditional WSGI servers

### Database

- **SQLAlchemy (2.0.23)** - SQL toolkit and ORM
  - Database-agnostic (supports SQLite, PostgreSQL, MySQL, etc.)
  - SQL query building and result mapping
  - Connection pooling for efficient database management
  - Prevents SQL injection through parameterized queries

### API Communication

- **Requests (2.31.0)** - HTTP library for making API calls
  - Simple and intuitive API for HTTP requests
  - Built-in timeout and retry mechanisms
  - Better error handling than urllib
  - Industry standard for Python HTTP requests

### Configuration Management

- **python-dotenv (1.0.0)** - Environment variable management
  - Loads credentials from `.env` file without committing to git
  - Security best practice for API keys and sensitive data
  - Easy configuration across different environments (dev, staging, prod)
  - Prevents hardcoding credentials in source code

### Why These Choices?

1. **Minimal Dependencies** - Kept only essential libraries to reduce complexity and security vulnerabilities
2. **Production-Ready** - All libraries are mature and widely used in production systems
3. **Easy to Extend** - Clean architecture allows easy addition of monitoring, authentication, etc.
4. **No Breaking Changes** - Pinned to stable versions to ensure reproducibility

## Project Structure

```
LiquidLabs_assignment/
├── app/
│   ├── db/
│   │   └── database.py          # Database setup, schema, and queries
│   ├── services/
│   │   └── services.py          # API client for Alpha Vantage
│   ├── utils/
│   │   └── utils.py             # Utility functions for data
│   ├── main.py                  # API end point, process request logic
│   ├── logger.py                # common logger
├── requirements.txt             # Python dependencies
├── .env.example                 # replace this with your env file
└── trade_data.db               # SQLite database
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd LiquidLabs_assignment
   ```

2. **Create virtual environment** (recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API credentials:

   ```
   API_KEY=your_alphavantage_api_key
   DATABASE_URL=sqlite:///./trade_data.db
   ```

   Get your free API key from [Alpha Vantage](https://www.alphavantage.co/)

5. **Run the application**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### Get Yearly Trading Summary

**Endpoint:**

```
GET /symbols/{symbol}/annual/{year}
```

**Parameters:**

- `symbol` (string, required): Stock symbol (e.g., "IBM", "AAPL")
- `year` (integer, required): Year to fetch data for

**Example Request:**

```bash
curl http://localhost:8000/symbols/IBM/annual/2025
```

**Success Response (200):**

```json
{
  "highest": 156.42,
  "lowest": 135.28,
  "total_volumn": 12345678900
}
```

**Error Response:**

```json
{
  "error": "Error Message"
}
```

## Database Schema

### monthly_data Table

```sql
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
```

### Indexes

```sql
CREATE INDEX idx_symbol_date ON monthly_data(symbol, date)
```

## How It Works

1. **Request Received** - User requests yearly trading summary for a stock symbol
2. **Cache Check** - System checks if data exists in database for that (symbol, year)
3. **Cache Hit** - If data exists, retrieves from database (fast)
4. **Cache Miss** - If data doesn't exist:
   - Calls Alpha Vantage API to fetch monthly data
   - Validates API response
   - Stores data in SQLite database
   - Updates cache tracking
5. **Calculation** - Calculates highest, lowest, and total volume for the year
6. **Response** - Returns summary statistics

## Error Handling

The application handles various error scenarios:

- **API Timeouts** - When Alpha Vantage takes too long to respond
- **Network Errors** - Connection failures and HTTP errors
- **Rate Limiting** - When API quota is exceeded
- **Invalid Data** - Malformed API responses or missing fields
- **Database Errors** - Database connection or write failures
- **Invalid Symbols** - Stock symbols not found in Alpha Vantage

All errors return appropriate HTTP status codes and descriptive error messages.

## Logging

Logs are stored in the `logs/` directory:

- **Console Output**: Real-time logging to terminal
- **File Logging**: Detailed logs saved to `logs/trading_summary_api.log`
- **Log Rotation**: Automatic rotation when log files reach 10MB

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

Example log locations:

```
logs/
└── trading_summary_api.log
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Alpha Vantage API Key (required)
API_KEY=your_api_key_here

# Database URL (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./trade_data.db
```

## Performance Considerations

1. **Database Caching** - Significantly reduces API calls for frequently accessed symbols
2. **Indexes** - Optimized queries with composite index on (symbol, date)
3. **Connection Pooling** - SQLAlchemy manages database connection pool
4. **Timeouts** - 10-second timeout on API requests prevents hanging

## Troubleshooting

### "API_KEY environment variable not found"

- Ensure `.env` file exists with `API_KEY` set
- Restart the application after adding environment variables

### "No data available for symbol"

- Verify the symbol is valid (e.g., "IBM", "AAPL")
- Check if Alpha Vantage API rate limit is exceeded (limit: 5 calls/minute)

The caching system helps minimize API calls. Consider upgrading for production use.

## Future Improvements

- Avoid calling Alpha Vantage API for invalid years. Create a timer to make API call to Alpha Vantage API and updated the database.

## License

This project is part of the LiquidLabs assignment.

## Support

For issues or questions, please contact the development team or open an issue in the repository.

---

**Last Updated**: April 29, 2026
