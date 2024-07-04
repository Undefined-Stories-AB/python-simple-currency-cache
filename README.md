# python-simple-currency-cache

`python-simple-currency-cache` is an in-house utility library designed to manage and cache currency exchange rates efficiently. This library provides functionalities to handle missing dates, fill empty currency rates, and cache these rates for quick retrieval.

## Features

- **Add Missing Dates**: Automatically fills in missing dates in a currency map.
- **Fill Empty Currencies**: Propagates the last known currency rate for dates where the rate is missing.
- **Cache Management**: Stores and retrieves currency rates from a cache for faster access.
- **Validation**: Ensures that currency data is consistent and complete before caching.

## Usage

Here is a basic example of how to use the `CurrencyCache` class:

```python
from currency_cache import CurrencyCache
from some_cache_api import CacheAPI

# Initialize cache API (example, implement your own CacheAPI)
cache_api = CacheAPI()

# Create an instance of CurrencyCache
currency_cache = CurrencyCache(cache_api, current_date="2024-07-04")

# Input data (example CSV data)
input_data = """
date;currency;rate
2024-07-01;USD;10.0
2024-07-02;USD;10.1
2024-07-03;USD;n/a
2024-07-04;USD;10.2
"""

# Cache all dates for a given currency
currency_cache.cache_all_dates(input_data, 'USD')

# Retrieve a cached currency rate
rate = currency_cache.try_get_currency_rate("2024-07-02", "USD", "SEK")
print(rate)  # Output: 10.1
```

## Methods

### `__init__(cache_api, current_date=None)`

- Initializes the `CurrencyCache` instance with a cache API and an optional current date.

### `add_missing_dates(currency_map)`

- Fills in missing dates in the provided currency map.

### `create_currency_map(dates, currencies)`

- Creates an ordered dictionary mapping dates to currency rates.

### `fill_empty_currencies_for_dates(currency_map)`

- Fills empty currency rates by propagating the last known rate.

### `cache_all_dates(input_data, currency_from)`

- Processes specific CSV formatted input data and caches all currency rates.

### `try_get_currency_rate(date_string, currency_from, currency_to='SEK')`

- Retrieves the cached currency rate for a given date and currency pair.

## CSV Data Format

The library expects input data in a specific CSV format with the following columns:

```
date;currency;rate
2024-07-01;USD;10.0
2024-07-02;USD;10.1
2024-07-03;USD;N/A
2024-07-04;USD;10.2
```

- **date**: The date in `YYYY-MM-DD` format.
- **currency**: The currency code (e.g., USD, EUR).
- **rate**: The exchange rate (or 'N/A' if not available.)

## License

This project is licensed under the MIT License.