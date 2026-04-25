import logging
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from db.connection import get_session
from db.models import Book, ScrapeState
from scraper.transform import BookModel

logger = logging.getLogger(__name__)


def load(books: list[BookModel], last_page: int) -> int:
    """
    Upsert validated books into the database and update scrape_state.

    Returns:
        Number of rows loaded (inserted or updated)
    """
    if not books:
        logger.info("No books to load.")
        return 0

    session = get_session()

    try:
        # TODO: build a list of dicts from the BookModel instances for bulk insert
        # Include scraped_at = datetime.now(timezone.utc)

        # TODO: construct an INSERT statement using sqlalchemy.dialects.postgresql.insert
        # Set ON CONFLICT (url) DO UPDATE for all non-key columns

        # TODO: execute the upsert inside the session transaction

        # TODO: update scrape_state.last_scraped_page and last_run_at
        # If no row exists yet, insert one

        session.commit()
        logger.info(f"Loaded {len(books)} books. Updated scrape_state to page {last_page}.")
        return len(books)

    except Exception as e:
        session.rollback()
        logger.error(f"Load failed, transaction rolled back: {e}")
        raise

    finally:
        session.close()
