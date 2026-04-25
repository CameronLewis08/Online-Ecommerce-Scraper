import pytest
from decimal import Decimal
from scraper.transform import BookModel

# NOTE: These tests require a test database.
# Set TEST_DATABASE_URL in your .env or use a pytest fixture that creates/tears down tables.

SAMPLE_BOOK = BookModel(
    title="A Light in the Attic",
    rating=3,
    price=Decimal("51.77"),
    category="Poetry",
    url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    availability="In stock",
)


class TestUpsertBehavior:
    def test_insert_new_book(self):
        # TODO: load [SAMPLE_BOOK], assert COUNT(*) FROM books == 1
        pass

    def test_upsert_same_url_no_duplicate(self):
        # TODO: load [SAMPLE_BOOK] twice, assert COUNT(*) FROM books == 1
        pass

    def test_upsert_updates_existing_data(self):
        # TODO: load SAMPLE_BOOK, then load a modified version with the same URL
        # Assert the updated fields are reflected in the DB row
        pass


class TestTransactionRollback:
    def test_failed_load_rolls_back(self):
        # TODO: mock the session.commit to raise an exception mid-load
        # Assert no rows were written to the database
        pass
