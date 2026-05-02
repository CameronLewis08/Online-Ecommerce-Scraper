from decimal import Decimal

from sqlalchemy import Integer, String, Numeric, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(128))
    url: Mapped[str] = mapped_column(String(255), unique=True)
    availability: Mapped[str] = mapped_column(String(50))
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    pipelinerun_id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20))
    rows_extracted: Mapped[int] = mapped_column(Integer, default=0)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0)
    rows_skipped: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str|None] = mapped_column(Text)

class ScrapeState(Base):
    __tablename__ = "scrape_state"

    scrapestate_id: Mapped[int] = mapped_column(primary_key=True)
    last_scraped_page: Mapped[str | None] = mapped_column(String(255))
    last_scraped_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
