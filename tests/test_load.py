import pytest
from decimal import Decimal
from db.connection import get_session

from db.models import Book
from scraper.load import load
from scraper.transform import BookModel

from unittest.mock import MagicMock, patch
from contextlib import contextmanager

SAMPLE_BOOK = BookModel(
    title="A Light in the Attic",
    rating=3,
    price=Decimal("51.77"),
    category="Poetry",
    url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    availability="In stock",
)

@pytest.fixture(autouse=True)
def clean_test_books():
    """Remove test book URLs before and after each test."""
    test_urls = [SAMPLE_BOOK.url]
    
    with get_session() as session:
        session.query(Book).filter(Book.url.in_(test_urls)).delete()
        session.commit()
    
    yield   # test runs here
    
    with get_session() as session:
        session.query(Book).filter(Book.url.in_(test_urls)).delete()
        session.commit()
        
class TestUpsertBehavior:
    def test_insert_new_book(self):
        
        load([SAMPLE_BOOK], category="Poetry", page=1)
        with get_session() as session:
            count = session.query(Book).filter_by(url=SAMPLE_BOOK.url).count()
        assert count == 1

    def test_upsert_same_url_no_duplicate(self):
        load([SAMPLE_BOOK], category="Poetry", page=1)
        load([SAMPLE_BOOK], category="Poetry", page=1)  # second load
        with get_session() as session:
            count = session.query(Book).filter_by(url=SAMPLE_BOOK.url).count()
        assert count == 1                

    def test_upsert_updates_existing_data(self):
        
        load([SAMPLE_BOOK], category="Poetry", page=1)

        updated = BookModel(
            title=SAMPLE_BOOK.title,
            rating=5,                    # changed from 3
            price=SAMPLE_BOOK.price,
            category=SAMPLE_BOOK.category,
            url=SAMPLE_BOOK.url,         # same URL — triggers conflict
            availability="Out of stock", # changed
        )
        load([updated], category="Poetry", page=1)

        with get_session() as session:
            book = session.query(Book).filter_by(url=SAMPLE_BOOK.url).first()
        assert book.rating == 5
        assert book.availability == "Out of stock"


class TestTransactionRollback:
    def test_failed_load_rolls_back(self):
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("Simulated DB failure")

        @contextmanager
        def mock_get_session():
            yield mock_session

        with patch("scraper.load.get_session", mock_get_session):
            with pytest.raises(Exception, match="Simulated DB failure"):
                load([SAMPLE_BOOK], category="Poetry", page=1)

        mock_session.rollback.assert_called_once()
