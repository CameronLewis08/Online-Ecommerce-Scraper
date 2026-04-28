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

    @field_validator("rating", mode="before")
    def validate_rating(cls, rating):
        if isinstance(rating, int):
            return rating
        if isinstance(rating, str):
            if rating in RATING_WORDS:
                return RATING_WORDS[rating]
            raise ValueError(f"Invalid rating word: {rating}")
        raise ValueError(f"Rating must be an int or a valid rating word, got {type(rating)}")

    @field_validator("price", mode="before")
    def validate_price(cls, price):
        if isinstance(price, Decimal):
            return price
        if isinstance(price, str):
            try:
                return Decimal(price.replace("£", "").strip())
            except InvalidOperation:
                raise ValueError(f"Invalid price format: {price}")
        raise ValueError(f"Price must be a Decimal or a string, got {type(price)}")


def transform(raw_books: list[dict]) -> tuple[list[BookModel], int]:
    """
    Validate and clean raw book dicts into BookModel instances.

    Returns:
        A tuple of (valid_models, skipped_count)
    """
    valid = []
    skipped = 0

    for raw in raw_books:
        try:
            valid.append(BookModel(**raw))
        except ValidationError as e:
            logger.warning(f"Skipping invalid book data: {raw} - Error: {e}")
            skipped += 1

    logger.info(f"Transform complete. {len(valid)} valid, {skipped} skipped.")
    return valid, skipped

