# Project Roadmap — E-Commerce ETL Pipeline

Check off tasks as you complete them. Each phase builds on the previous one.
Reference BEST_PRACTICES.md when making decisions. Ask for help on any task.

---

## Phase 1 — Project Setup

- [ ] Create and activate a Python virtual environment (`python -m venv venv`)
- [ ] Install dependencies and verify `requirements.txt` is pinned to exact versions
- [ ] Copy `.env.example` to `.env` and fill in your local Postgres credentials
- [ ] Verify you can connect to Postgres (run `psql` or a quick Python test)
- [ ] Confirm `.env` is listed in `.gitignore` before making any commits

**Checkpoint:** `python -c "from config.settings import settings; print(settings.db_url)"` prints your DB URL without errors.

---

## Phase 2 — Database Layer

- [ ] Write SQLAlchemy ORM models in `db/models.py` for all three tables:
  - `books` (id, title, rating, price, category, url, availability, scraped_at)
  - `pipeline_runs` (id, started_at, completed_at, status, rows_extracted, rows_loaded, rows_skipped, error_message)
  - `scrape_state` (id, last_scraped_page, last_run_at)
- [ ] Write `db/connection.py` — engine creation and session factory using `python-dotenv` settings
- [ ] Write a table creation script that calls `Base.metadata.create_all(engine)`
- [ ] Run the script and verify all three tables exist in Postgres (`\dt` in psql)
- [ ] Add a `UNIQUE` constraint on `books.url`

**Checkpoint:** Tables exist in Postgres. Running the creation script a second time does not error (idempotent).

---

## Phase 3 — Extract

- [ ] Inspect `books.toscrape.com` in your browser — find the HTML elements for title, rating, price, category, and URL
- [ ] Write `scraper/extract.py` — scrape a single page and return a list of raw dicts
- [ ] Add pagination — loop through all pages until there are no more
- [ ] Read `scrape_state` at the start so the scraper resumes from the last page, not page 1
- [ ] Add `time.sleep(1)` between page requests
- [ ] Set a descriptive `User-Agent` header in your requests session
- [ ] Add INFO-level logging for each page scraped

**Checkpoint:** Running `extract.py` directly returns raw book dicts. Running it twice starts from where it left off.

---

## Phase 4 — Transform

- [ ] Define a Pydantic model in `scraper/transform.py` with correct types for each field
- [ ] Write a `transform()` function that converts a list of raw dicts into validated Pydantic models
- [ ] Handle the rating — `books.toscrape.com` uses words ("One", "Two", "Three"...) — convert to int 1–5
- [ ] Handle the price — strip the "£" symbol and convert to a `Decimal`
- [ ] Catch Pydantic `ValidationError` per row, log a WARNING, and count skipped rows — do not crash
- [ ] Return both the valid models and a count of skipped rows

**Checkpoint:** Passing a dict with a missing or malformed field logs a warning and returns 0 valid models for that row, not an exception.

---

## Phase 5 — Load

- [ ] Write `scraper/load.py` — takes a list of validated Pydantic models and loads them into Postgres
- [ ] Implement upsert logic: `INSERT INTO books ... ON CONFLICT (url) DO UPDATE SET ...`
- [ ] Wrap the batch insert in a transaction — if it fails mid-batch, it rolls back
- [ ] After a successful load, update `scrape_state.last_scraped_page` and `last_run_at`
- [ ] Return the count of rows loaded

**Checkpoint:** Running load twice with the same data results in the same number of rows in the DB (no duplicates). Check with `SELECT COUNT(*) FROM books`.

---

## Phase 6 — Pipeline Orchestration

- [ ] Write `scraper/pipeline.py` — calls `extract()` → `transform()` → `load()` in sequence
- [ ] At pipeline start: insert a `pipeline_runs` row with `status='running'` and `started_at=now()`
- [ ] At pipeline end: update that row with `completed_at`, final counts, and `status='success'`
- [ ] If any step raises an unhandled exception: update the run row with `status='failed'` and `error_message`
- [ ] Set up logging in `pipeline.py` to write to both stdout and `logs/pipeline.log`
- [ ] Use a `RotatingFileHandler` so log files don't grow forever

**Checkpoint:** After one run, `SELECT * FROM pipeline_runs` shows one row with correct counts and `status='success'`. Intentionally break something and verify `status='failed'` with an error message.

---

## Phase 7 — Scheduler

- [ ] Write `scheduler.py` — sets up APScheduler to call `pipeline.run()` on a configurable interval
- [ ] Make the interval configurable via `.env` (e.g. `SCRAPE_INTERVAL_MINUTES=60`)
- [ ] Add a log message when the scheduler starts and when each job fires
- [ ] Run `scheduler.py` and leave it running — verify the pipeline executes on schedule
- [ ] Verify `pipeline_runs` accumulates new rows for each scheduled execution

**Checkpoint:** Leaving the scheduler running for two intervals produces two rows in `pipeline_runs`.

---

## Phase 8 — Testing

- [ ] Write unit tests in `tests/test_transform.py`:
  - Test valid input returns correct Pydantic model
  - Test "Three" rating converts to int 3
  - Test "£12.99" price converts to Decimal 12.99
  - Test a row missing a required field is skipped (not a crash)
- [ ] Write unit tests in `tests/test_load.py`:
  - Test that loading the same URL twice results in one row (upsert works)
  - Use a test database or mock the SQLAlchemy session
- [ ] Run `pytest` and verify all tests pass

**Checkpoint:** `pytest` passes with no failures. Coverage covers all transform normalization logic.

---

## Phase 9 — Docker (Optional — complete last)

- [ ] Write a `Dockerfile` for the scraper service (base: `python:3.11-slim`)
- [ ] Write `docker-compose.yml` with two services: `postgres` and `scraper`
- [ ] Configure the scraper service to wait for Postgres to be ready before starting
- [ ] Test: `docker compose up` runs the full pipeline end-to-end in containers
- [ ] Verify `pipeline_runs` has data after the container run

**Checkpoint:** `docker compose up` from a clean environment runs the pipeline with zero manual setup.

---

## Final Review Checklist

- [ ] `.env` is NOT committed to git
- [ ] `requirements.txt` has exact pinned versions
- [ ] All three tables exist and are populated after a full run
- [ ] `pipeline_runs` has entries for every run with correct status
- [ ] No `print()` statements — all output goes through the logger
- [ ] README explains what the project does, how to set it up, and how to run it
- [ ] You can answer every question in `DEFINITION_OF_DONE.md`
