import time
import logging
import requests
from bs4 import BeautifulSoup
from config.settings import settings

logger = logging.getLogger(__name__)

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_last_scraped_page() -> int:
    """Read the watermark from scrape_state. Returns 1 if no state exists yet."""
    # TODO: query ScrapeState from the database and return last_scraped_page
    # If no row exists, return 1
    pass


def scrape_page(page: int) -> list[dict]:
    """Fetch one page of books and return a list of raw dicts."""
    # TODO:
    # 1. Build the URL for the given page number
    # 2. GET the page with a descriptive User-Agent header
    # 3. Parse HTML with BeautifulSoup
    # 4. Find all book elements and extract: title, rating, price, category, url, availability
    # 5. Return a list of raw dicts (do NOT validate here — that is Transform's job)
    pass


def extract() -> list[dict]:
    """Scrape all pages starting from the last scraped page. Returns raw book dicts."""
    start_page = get_last_scraped_page()
    all_books = []
    page = start_page

    logger.info(f"Starting extraction from page {start_page}")

    while True:
        # TODO: scrape the page, break if no results (end of catalogue)
        # Log each page, sleep between requests, increment page counter
        pass

    logger.info(f"Extraction complete. {len(all_books)} raw records collected.")
    return all_books
