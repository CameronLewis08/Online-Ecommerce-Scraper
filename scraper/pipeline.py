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
    root_logger = logging.getLogger()
    if root_logger.handlers:        # already configured — don't add duplicates
        return
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file, maxBytes=settings.log_max_bytes, backupCount=settings.log_backup_count
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)          # ← missing
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stream_handler)        # ← missing
    root_logger.addHandler(file_handler)          # ← missing 



def run() -> None:

    # Insert the initial run record and get its ID
    with get_session() as session:
        run_record = PipelineRun(started_at=datetime.now(timezone.utc), status="running")
        session.add(run_record)
        session.commit()
        run_id = run_record.pipelinerun_id      # save the ID before session closes

    rows_extracted = rows_loaded = rows_skipped = 0

    try:
        raw_books, last_category, last_page = extract()
        rows_extracted = len(raw_books)

        valid_books, rows_skipped = transform(raw_books)

        rows_loaded = load(valid_books, last_category, last_page)

        with get_session() as session:
            record = session.get(PipelineRun, run_id)
            record.status = "success"
            record.completed_at = datetime.now(timezone.utc)
            record.rows_extracted = rows_extracted
            record.rows_loaded = rows_loaded
            record.rows_skipped = rows_skipped
            session.commit()

        logger.info(f"Pipeline complete. Extracted={rows_extracted}, Loaded={rows_loaded}, Skipped={rows_skipped}")

    except Exception as e:
        with get_session() as session:
            record = session.get(PipelineRun, run_id)
            record.status = "failed"
            record.completed_at = datetime.now(timezone.utc)
            record.error_message = str(e)
            session.commit()

        logger.error(f"Pipeline failed: {e}", exc_info=True)
