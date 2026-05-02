
from datetime import datetime 
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from config.settings import settings
from db.connection import create_tables
from scraper.pipeline import setup_logging, run

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    create_tables()  # ensure tables exist before first run
    logger.info(f"Scheduler starting. Pipeline will run every {settings.scrape_interval_minutes} minute(s).")

    scheduler = BlockingScheduler()

    scheduler.add_job(run, 'interval', minutes=settings.scrape_interval_minutes, next_run_time=datetime.now())
    
    scheduler.start()



if __name__ == "__main__":
    main()
