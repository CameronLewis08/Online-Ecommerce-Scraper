import logging
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, field_validator, ValidationError

logger = logging.getLogger(__name__)

RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BookModel(BaseModel):
    title: str
    rating: int
    price: Decimal
    category: str
    url: str
    availability: str

    # TODO: add a @field_validator for 'rating' that converts word strings to ints
    # e.g. "Three" -> 3. Raise ValueError if the word is not in RATING_WORDS.

    # TODO: add a @field_validator for 'price' that strips the '£' symbol
    # and converts to Decimal. Raise ValueError if conversion fails.


def transform(raw_books: list[dict]) -> tuple[list[BookModel], int]:
    """
    Validate and clean raw book dicts into BookModel instances.

    Returns:
        A tuple of (valid_models, skipped_count)
    """
    valid = []
    skipped = 0

    for raw in raw_books:
        # TODO: attempt to parse raw dict into BookModel
        # On ValidationError: log a WARNING with the raw data and error, increment skipped
        pass

    logger.info(f"Transform complete. {len(valid)} valid, {skipped} skipped.")
    return valid, skipped
