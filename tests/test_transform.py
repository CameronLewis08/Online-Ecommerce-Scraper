import pytest
from decimal import Decimal
from scraper.transform import transform, BookModel

VALID_RAW = {
    "title": "A Light in the Attic",
    "rating": "Three",
    "price": "£51.77",
    "category": "Poetry",
    "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "availability": "In stock",
}


class TestRatingConversion:
    def test_word_to_int(self):
        # TODO: assert that "Three" becomes 3
        pass

    def test_all_rating_words(self):
        # TODO: parametrize or loop through One→1, Two→2, Three→3, Four→4, Five→5
        pass

    def test_invalid_rating_is_skipped(self):
        # TODO: pass a raw dict with rating="Six", assert skipped=1 and valid=[]
        pass


class TestPriceConversion:
    def test_strips_currency_symbol(self):
        # TODO: assert that "£51.77" becomes Decimal("51.77")
        pass

    def test_invalid_price_is_skipped(self):
        # TODO: pass a raw dict with price="not-a-price", assert skipped=1
        pass


class TestTransformFunction:
    def test_valid_row_returns_model(self):
        # TODO: call transform([VALID_RAW]) and assert len(valid)==1, skipped==0
        pass

    def test_empty_input_returns_empty(self):
        # TODO: call transform([]) and assert valid==[], skipped==0
        pass

    def test_mixed_valid_invalid_counts_correctly(self):
        # TODO: pass one valid and one invalid raw dict, assert valid==1, skipped==1
        pass
