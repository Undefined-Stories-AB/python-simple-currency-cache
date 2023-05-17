import asyncio
import os
import requests
import urllib.parse
from pathlib import Path
from diskcache import Cache

from simple_currency_cache.currency_cache import CurrencyCache


async def fetch_from_riksbanken(cache: Cache, date_from: str, date_to: str, verbose: bool = False):
    currency_cache = CurrencyCache(cache, date_to)

    currencies = ["EUR", "USD"]
    currency_range_key = f"{'+'.join(currencies)}_{date_from}_{date_to}"
    _, has_currency_range = cache.peek(currency_range_key, ("", False))

    if verbose:
        if has_currency_range:
            print("Currency for date range exists in cache, skipping.")
            return
        print(f"Currency for date range is missing in cache, fetching: {date_from} -> {date_to}.")
    elif has_currency_range:
        return

    currency_to = "SEK"

    def get_url(currency_from):
        url = "https://www.riksbank.se/sv/statistik/sok-rantor--valutakurser/"
        query_params = {
            "c": "cAverage",
            "f": "Day",
            "from": date_from,
            "to": date_to,
            f"g130-{currency_to}{currency_from}PMI": "on",
            "s": "Dot",
            "export": "csv",
        }
        return url + "?" + urllib.parse.urlencode(query_params)

    for currency in currencies:
        url = get_url(currency)
        response = requests.get(
            url,
            headers={
                "Content-Type": "*/*",
            }
        )
        if response.status_code != 200:
            raise ValueError(
                f"Failed to fetch currencies from Riksbanken for interval: {date_from} -> {date_to} - {response.status_code}"
            )

        data = response.text
        #print(f"Fetched: {data}")
        currency_cache.cache_all_dates(data, currency)

    cache.add(currency_range_key, True)


async def main():
    cache_path = os.path.join(Path.cwd(), ".cache", "riksbanken")
    cache = Cache(cache_path)
    currency_cache = CurrencyCache(cache)
    await fetch_from_riksbanken(cache, "2023-01-01", "2023-01-31", verbose=True)

    print(currency_cache.try_get_currency_rate("2023-01-15", "EUR"))


if __name__ == "__main__":
    asyncio.run(main())
