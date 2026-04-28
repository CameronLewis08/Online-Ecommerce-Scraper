import logging
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from db.connection import get_session
from db.models import Book, ScrapeState
from scraper.transform import BookModel

logger = logging.getLogger(__name__)


def load(books: list[BookModel], category: str, page: int) -> int:
    """
    Upsert validated books into the database and update scrape_state.

    Returns:
        Number of rows loaded (inserted or updated)
    """
    if not books:
        logger.info("No books to load.")
        return 0
    
    watermark = f"{category}:{page}"
    

    with get_session() as session:
        try:
            # TODO: build a list of dicts from the BookModel instances for bulk insert
            # Include scraped_at = datetime.now(timezone.utc)
            book_dicts = []
            now = datetime.now(timezone.utc)
            for book in books:
                book_dicts.append({
                    "title": book.title,
                    "rating": book.rating,
                    "price": book.price,
                    "category": book.category,
                    "url": book.url,
                    "availability": book.availability,
                    "scraped_at": now
                })

            # TODO: construct an INSERT statement using sqlalchemy.dialects.postgresql.insert
            # Set ON CONFLICT (url) DO UPDATE for all non-key columns
            stmt = insert(Book).values(book_dicts)
            update_cols = {col.name: col for col in stmt.excluded if col.name != "book_id" and col.name != "url"}  # exclude primary key and url from update
            stmt = stmt.on_conflict_do_update(
                index_elements=["url"],
                set_=update_cols
            )

            # TODO: execute the upsert inside the session transaction
            session.execute(stmt)

            # TODO: update scrape_state.last_scraped_page and last_run_at
            # If no row exists yet, insert one

            existing_state = session.query(ScrapeState).first()
            if existing_state:
                existing_state.last_scraped_page = watermark
                existing_state.last_scraped_at = now
            else:
                new_state = ScrapeState(last_scraped_page=watermark, last_scraped_at=now)
                session.add(new_state)
            
            session.commit()
            logger.info(f"Loaded {len(books)} books. Updated scrape_state to page {watermark}.")
            return len(books)

        except Exception as e:
            session.rollback()
            logger.error(f"Load failed, transaction rolled back: {e}")
            raise
if __name__ == "__main__":
    from decimal import Decimal
    from scraper.transform import BookModel

    test_books = [
        BookModel(
            title="A Test Book",
            rating=3,
            price=Decimal("12.99"),
            category="Travel",
            url="https://books.toscrape.com/catalogue/a-test-book_1/index.html",
            availability="In stock",
        ),
        BookModel(
            title="Another Test Book",
            rating=5,
            price=Decimal("9.99"),
            category="Travel",
            url="https://books.toscrape.com/catalogue/another-test-book_2/index.html",
            availability="In stock",
        ),
    ]

    loaded = load(test_books, category="Travel", page=1)
    print(f"Loaded: {loaded} rows")