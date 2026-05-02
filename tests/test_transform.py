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
        
        book = BookModel(**VALID_RAW)
        assert book.rating == 3

    def test_all_rating_words(self):
        
        for word, expected in [("One", 1), ("Two", 2), ("Three", 3), ("Four", 4), ("Five", 5)]:
            raw = VALID_RAW.copy()
            raw["rating"] = word
            book = BookModel(**raw)
            assert book.rating == expected

    def test_invalid_rating_is_skipped(self):
        
        raw = {**VALID_RAW, "rating": "Six"}
        valid, skipped = transform([raw])
        assert skipped == 1
        assert valid == []


class TestPriceConversion:
    def test_strips_currency_symbol(self):
        
        book = BookModel(**VALID_RAW)
        assert book.price == Decimal("51.77")

    def test_invalid_price_is_skipped(self):
        
        raw = {**VALID_RAW, "price": "not-a-price"}
        valid, skipped = transform([raw])
        assert skipped == 1
        assert valid == []


class TestTransformFunction:
    def test_valid_row_returns_model(self):
        
        valid, skipped = transform([VALID_RAW])
        assert len(valid) == 1
        assert skipped == 0
        
    def test_empty_input_returns_empty(self):
        
        valid, skipped = transform([])
        assert valid == []
        assert skipped == 0


    def test_mixed_valid_invalid_counts_correctly(self):
        
        invalid_raw = {**VALID_RAW, "rating": "Six", "url": "https://example.com/other"}  # also change URL to avoid duplicate key if both valid and invalid are transformed
        valid, skipped = transform([VALID_RAW, invalid_raw])
        assert len(valid) == 1
        assert skipped == 1
