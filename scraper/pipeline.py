import logging
import logging.handlers
from datetime import datetime, timezone
from config.settings import settings
from db.connection import get_session
from db.models import PipelineRun
from scraper.extract import extract
from scraper.transform import transform
from scraper.load import load

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure logging to stdout and a rotating file."""
    # TODO: create a formatter with timestamp, level, and message
    # TODO: add a StreamHandler (stdout) at INFO level
    # TODO: add a RotatingFileHandler pointed at settings.log_file
    #       with maxBytes=settings.log_max_bytes, backupCount=settings.log_backup_count
    # TODO: attach both handlers to the root logger
    pass


def run() -> None:
    """Execute one full ETL run and record the result in pipeline_runs."""
    session = get_session()
    run_record = PipelineRun(started_at=datetime.now(timezone.utc), status="running")

    # TODO: add run_record to session and commit to get its ID

    rows_extracted = 0
    rows_loaded = 0
    rows_skipped = 0

    try:
        raw_books = extract()
        rows_extracted = len(raw_books)

        valid_books, rows_skipped = transform(raw_books)

        # TODO: get last_page from scrape_state so load() can update the watermark
        last_page = 1

        rows_loaded = load(valid_books, last_page)

        # TODO: update run_record: status='success', completed_at, all row counts
        session.commit()
        logger.info(f"Pipeline complete. Extracted={rows_extracted}, Loaded={rows_loaded}, Skipped={rows_skipped}")

    except Exception as e:
        # TODO: update run_record: status='failed', completed_at, error_message=str(e)
        session.commit()
        logger.error(f"Pipeline failed: {e}", exc_info=True)

    finally:
        session.close()
