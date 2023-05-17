from datetime import datetime, timedelta
from typing import Literal, OrderedDict

class CurrencyCache:
    current_date: str
    def __init__(self, cache_api, current_date: str | None = None):
        self.cache_api = cache_api

        if isinstance(current_date, str):
            self.current_date = current_date
        else:
            self.current_date = datetime.now().strftime("%Y-%m-%d")

    def add_missing_dates(self, currency_map: OrderedDict[str, str]) -> OrderedDict[str, str]:
        first_date_string = next(iter(currency_map))
        last_date_string = list(currency_map)[-1]

        if not first_date_string.startswith('20'):
            raise ValueError('Could not find first date in list while adding missing dates')

        if not last_date_string.startswith('20'):
            raise ValueError('Could not find last date in list while adding missing dates')

        first_date = datetime.strptime(first_date_string, '%Y-%m-%d')
        last_date = datetime.strptime(last_date_string, '%Y-%m-%d')

        # Calculate the time difference in days between the
        # first date and up to and including the target date
        days_diff = (last_date + timedelta(days=1) - first_date).days

        if days_diff <= 1 or days_diff > 356:
            raise ValueError(
                f'Unexpected difference in days: {days_diff} - {first_date_string} -> {last_date_string}, exiting'
            )

        result: OrderedDict[str, str] = {}
        for i in range(days_diff):
            new_date = first_date + timedelta(days=i)
            new_date_string = new_date.strftime('%Y-%m-%d')
            currency_rate = currency_map.get(new_date_string, None)
            # We don't keep the last date of the file if currency rate is missing or is not 'n/a'
            # since we can't be sure if the currency rate should be defined or not yet
            if new_date == last_date and currency_rate is None:
                continue
            result[new_date_string] = currency_rate

        assert list(result.values())[0] is not None
        assert list(result.values())[-1] is not None

        return result

    def create_currency_map(self, dates: list[str], currencies: list[str]) -> OrderedDict[str, str]:
        result: OrderedDict[str, str] = {}
        for i,date in enumerate(dates):
            result[date] = currencies[i]
        return result

    def fill_empty_currencies_for_dates(self, currency_map: OrderedDict[str, str])-> OrderedDict[str, str]:
        sorted_dates = sorted(currency_map.keys())

        previous_currency = None
        result: OrderedDict[str, str] = {}
        for date in sorted_dates:
            currency = currency_map.get(date)
            if currency:
                result[date] = currency
                previous_currency = currency
            else:
                result[date] = previous_currency

        return result

    def cache_all_dates(self, input_data, currency_from):
        rows = input_data.strip().split('\n')[1:]

        dates = [row.split(';')[0] for row in rows]
        currencies = [row.split(';')[3].strip() for row in rows]

        last_date_string = dates[-1]
        last_currency = currencies[-1]


        if last_currency == 'n/a':
            if last_date_string != self.current_date:
                raise ValueError(f"Expected last row of riksbanken csv to contain current date: '{self.current_date}', instead got: '{last_date_string}, {rows[-1]}'")

            now = datetime.now()
            if now.hour > 13 and now.minute > 20:
                raise ValueError(f"Expected riksbanken currency rate for '{last_date_string}' to be defined after 13:00, instead got: 'n/a'")

        currency_map = self.create_currency_map(dates, currencies)
        currency_map = self.add_missing_dates(currency_map)
        currency_map = self.fill_empty_currencies_for_dates(currency_map)

        start_date = datetime.strptime(dates[0], '%Y-%m-%d')
        end_date = datetime.strptime(last_date_string, '%Y-%m-%d')

        if end_date > datetime.strptime(self.current_date, '%Y-%m-%d') or start_date >= end_date:
            raise ValueError(f"Unexpected range while caching currency rate for dates: {start_date} -> {end_date}")

        for date_string, currency_rate in currency_map.items():
            cache_key = f"{currency_from}-SEK_{date_string}"

            if currency_rate and currency_rate != 'n/a':
                self.cache_api.add(cache_key, currency_rate)
            elif currency_rate != 'n/a':
                error_message = f"Failed to cache currency: {cache_key}. {{'dateString': {date_string}, 'currencyRate': {currency_rate}}}"
                print(error_message)

    def try_get_currency_rate(self, date_string: str, currency_from: Literal['EUR'] | Literal['USD'], currency_to: Literal['SEK'] = 'SEK') -> str:
        currency_cache_key = f"{currency_from}-{currency_to}_{date_string}"

        currency_rate = self.cache_api.get(currency_cache_key)
        if not isinstance(currency_rate, str):
            raise ValueError(f"Expected currency rate to be a string, instead got: {currency_rate}")
        return currency_rate


if __name__ == "__main__":

    pass