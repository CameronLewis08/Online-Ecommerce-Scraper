from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    # TODO: define columns
    # id, title, rating (int), price (Numeric), category, url (unique), availability, scraped_at


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    # TODO: define columns
    # id, started_at, completed_at, status, rows_extracted, rows_loaded, rows_skipped, error_message


class ScrapeState(Base):
    __tablename__ = "scrape_state"

    # TODO: define columns
    # id, last_scraped_page (int), last_run_at
