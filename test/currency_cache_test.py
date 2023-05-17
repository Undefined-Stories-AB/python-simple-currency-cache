import datetime
from typing import OrderedDict
import unittest

from simple_currency_cache.currency_cache import CurrencyCache


class CurrencyCacheTests(unittest.TestCase):
    def setUp(self):
        # Create a mock CacheApi object for testing
        self.cache_api = MockCacheApi()
        self.currency_cache = CurrencyCache(self.cache_api, current_date="2023-05-15")

    def test_add_missing_dates(self):
        currency_map = {"2023-05-10": "1.2", "2023-05-12": "1.3", "2023-05-15": "n/a"}

        expected_result = {
            "2023-05-10": "1.2",
            "2023-05-11": None,
            "2023-05-12": "1.3",
            "2023-05-13": None,
            "2023-05-14": None,
            "2023-05-15": "n/a",
        }

        result = self.currency_cache.add_missing_dates(currency_map)
        self.assertEqual(result, expected_result)

    def test_fill_empty_currencies_for_dates(self):
        currency_map = {
            "2023-05-10": "1.2",
            "2023-05-11": None,
            "2023-05-12": None,
            "2023-05-13": "1.3",
            "2023-05-14": None,
            "2023-05-15": "n/a",
        }

        expected_result = {
            "2023-05-10": "1.2",
            "2023-05-11": "1.2",
            "2023-05-12": "1.2",
            "2023-05-13": "1.3",
            "2023-05-14": "1.3",
            "2023-05-15": "n/a",
        }

        result = self.currency_cache.fill_empty_currencies_for_dates(currency_map)
        self.assertEqual(result, expected_result)

    def test_cache_up_to_current_date(self):
        expected_currencies = OrderedDict(
            [
                ("EUR-SEK_2023-05-10", "1.2"),
                ("EUR-SEK_2023-05-11", "1.2"),
                ("EUR-SEK_2023-05-12", "1.3"),
                ("EUR-SEK_2023-05-13", "1.3"),
                ("EUR-SEK_2023-05-14", "1.3"),
            ]
        )
        # NOTE: 'n/a' implies that the currency rate is not yet determined; we expect it to be either
        # empty or a float value
        input_data = f"date;;;currency_rate\n2023-05-10;;;1.2\n2023-05-12;;;1.3\n2023-05-15;;;n/a"
        currency_from = "EUR"

        # We would always expect value of current date
        # to be defined as currency rate or empty
        # after 13:20 Swedish Local Time
        now = datetime.datetime.now()
        if now.hour > 13 and now.minute > 20:
            with self.assertRaises(Exception) as context:
                self.currency_cache.cache_all_dates(input_data, currency_from)
                self.assertTrue(f"Expected riksbanken currency rate for '2023-05-15' to be defined after 13:00, instead got: 'n/a'" in context.exception)
            input_data = f"date;;;currency_rate\n2023-05-10;;;1.2\n2023-05-12;;;1.3\n2023-05-15;;;1.4"
            expected_currencies["EUR-SEK_2023-05-15"] = "1.4"

        self.currency_cache.cache_all_dates(input_data, currency_from)

        self.assertEqual(self.cache_api.currencies, expected_currencies)

    def test_cache_up_to_previous_date(self):
        input_data = f"date;;;currency_rate\n2023-05-10;;;1.2\n2023-05-12;;;1.3\n2023-05-14;;;"
        currency_from = "EUR"
        self.currency_cache.cache_all_dates(input_data, currency_from)
        self.assertEqual(
            self.cache_api.currencies,
            OrderedDict(
                [
                    ("EUR-SEK_2023-05-10", "1.2"),
                    ("EUR-SEK_2023-05-11", "1.2"),
                    ("EUR-SEK_2023-05-12", "1.3"),
                    ("EUR-SEK_2023-05-13", "1.3"),
                    ("EUR-SEK_2023-05-14", "1.3"),
                ]
            ),
        )


class MockCacheApi:
    currencies: OrderedDict[str, str]

    def __init__(self):
        self.currencies = OrderedDict()

    def add(self, cache_key: str, currency_rate: str):
        self.currencies[cache_key] = currency_rate
    def peek(self, cache_key: str, currency_rate: str):
        self.currencies[cache_key] = currency_rate



if __name__ == "__main__":
    unittest.main()
