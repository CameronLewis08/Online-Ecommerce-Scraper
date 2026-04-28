import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    db_url: str = os.getenv("DATABASE_URL", "")
    scrape_base_url: str = os.getenv("SCRAPE_BASE_URL", "https://books.toscrape.com")
    scrape_interval_minutes: int = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "60"))
    request_delay_seconds: float = float(os.getenv("REQUEST_DELAY_SECONDS", "1.0"))
    log_file: str = os.getenv("LOG_FILE", "logs/pipeline.log")
    log_max_bytes: int = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))


settings = Settings()
