from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings
from db.models import Base


# TODO: create the engine using settings.db_url
# Hint: create_engine(settings.db_url, pool_size=5, max_overflow=10)
engine = None

# TODO: create a SessionLocal factory bound to the engine
# Hint: sessionmaker(bind=engine, autocommit=False, autoflush=False)
SessionLocal = None


def create_tables() -> None:
    """Create all tables if they do not already exist."""
    # TODO: call Base.metadata.create_all(engine)
    pass


def get_session() -> Session:
    """Return a new database session. Caller is responsible for closing it."""
    # TODO: return SessionLocal()
    pass
