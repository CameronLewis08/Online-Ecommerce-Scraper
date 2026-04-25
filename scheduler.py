import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from config.settings import settings
from scraper.pipeline import setup_logging, run

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    logger.info(f"Scheduler starting. Pipeline will run every {settings.scrape_interval_minutes} minute(s).")

    scheduler = BlockingScheduler()

    # TODO: add a job that calls run() on an interval_trigger using settings.scrape_interval_minutes
    # Run once immediately at start, then on the schedule

    # TODO: start the scheduler
    pass


if __name__ == "__main__":
    main()
