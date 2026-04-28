
import time
import logging
import requests
from bs4 import BeautifulSoup
from config.settings import settings
from urllib.parse import urljoin

from db.connection import get_session
from db.models import ScrapeState

logger = logging.getLogger(__name__)


def get_categories() -> list[dict]:
    """Read the categories from the database. Returns a list of category dictionaries."""
    # TODO: query categories from the database and return a list of category dicts
    response = requests.get("https://books.toscrape.com/catalogue/category/books_1/", headers={"User-Agent": "EcommerceETL-Portfolio/1.0 (educational project)"})
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    category_list = soup.find("ul", class_="nav-list").find("ul").find_all("li")
    categories = []
    for category in category_list:
        name = category.a.text.strip()
        relative_url = urljoin("https://books.toscrape.com/catalogue/category/books/", category.a["href"])
        categories.append({"name": name, "url": relative_url})

    logger.info(f"Found {len(categories)} categories.")

    return categories

def get_last_scraped_page() -> tuple[str | None, int]:
    """
    Read the watermark from scrape_state.
    Returns (last_category, last_page) or (None, 1) if no state exists.
    """
    with get_session() as session:
        state = session.query(ScrapeState).first()
        if state is None or state.last_scraped_page is None:
            return None, 1

        category, page = state.last_scraped_page.split(":")
        return category, int(page)

def scrape_category_page(category: str, category_url: str, page: int) -> tuple[list[dict], bool]:
    """Fetch one page of books and return a list of raw dicts."""
    # TODO:
    # 1. Build the URL for the given page number
    # 2. GET the page with a descriptive User-Agent header
    # 3. Parse HTML with BeautifulSoup
    # 4. Find all book elements and extract: title, rating, price, category, url, availability
    # 5. Return a list of raw dicts (do NOT validate here — that is Transform's job)

    if page == 1:
        url = category_url                                        
    else:
        url = category_url.replace("index.html", f"page-{page}.html")

    response = requests.get(
        url,
        headers={"User-Agent": "EcommerceETL-Portfolio/1.0 (educational project)"}
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    ol = soup.find("ol", class_="row")
    if not ol:
        return [], False

    books = []

    articles = ol.find_all("article", class_="product_pod")
    for book in articles:
        image = book.find("div", class_="image_container").find("img")
        title = image.attrs["alt"]
        rating = book.p["class"][1]
        price = book.select_one("p.price_color").text.strip()
        relative_url = book.h3.a["href"]
        availability = book.select_one("p.instock.availability").text.strip()

        books.append({
            "title": title,
            "rating": rating,
            "price": price,
            "category": category,       # ← comes from the parameter, not the HTML
            "url": urljoin(response.url, relative_url),
            "availability": availability,
        })

    logger.info(f"Scraped {len(books)} books in '{category}' from {url}")

    has_next = soup.find("li", class_="next") is not None   # ← check for next button
    return books, has_next



def extract() -> list[dict]:
    categories = get_categories()
    all_books = []

    last_category, last_page = get_last_scraped_page()
    found_resume_point = last_category is None

    for cat in categories:
        if not found_resume_point:
            if cat["name"] != last_category:
                continue            # skip categories before the resume point
            found_resume_point = True
            start_page = last_page + 1  # resume from the next page
        else:
            start_page = 1

        page = start_page
        while True:
            books, has_next = scrape_category_page(cat["name"], cat["url"], page)
            all_books.extend(books)
            logger.info(f"  Page {page} — {len(books)} books")
            
            if not has_next or not books:
                break                    # stop before requesting a page that doesn't exist
            
            time.sleep(settings.request_delay_seconds)
            page += 1

    logger.info(f"Extraction complete. {len(all_books)} raw records collected.")
    return all_books
