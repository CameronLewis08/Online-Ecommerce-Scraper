# Online Ecommerce Scraper

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-red)
![APScheduler](https://img.shields.io/badge/APScheduler-3.11-green)

A production-style ETL pipeline that scrapes book data from [books.toscrape.com](https://books.toscrape.com), validates and transforms it, and loads it into PostgreSQL. Runs on a configurable schedule with full observability via a pipeline audit log.

---

## Skills Demonstrated

- **ETL pipeline design** — clean separation of Extract, Transform, and Load phases, each independently testable
- **Incremental scraping with watermarks** — resumes from the last scraped page across runs using a `scrape_state` table
- **Idempotent upserts** — `INSERT ... ON CONFLICT DO UPDATE` prevents duplicate rows on re-runs
- **Pydantic v2 validation** — per-row validation with graceful skipping of malformed records
- **Transactional loading** — batch inserts wrapped in a single transaction; failed batches roll back atomically
- **Pipeline observability** — every run recorded in `pipeline_runs` with row counts, timing, and error messages
- **Scheduled execution** — APScheduler runs the pipeline on a configurable interval without OS-level cron
- **Containerization** — Docker Compose setup with health-checked Postgres dependency
- **Rotating log files** — `RotatingFileHandler` prevents unbounded log growth

---

## Architecture

```
Scheduler (APScheduler)
    └── pipeline.run()
            ├── extract()  ──→ books.toscrape.com (all categories, paginated)
            │       └── reads ─── scrape_state  (resume watermark)
            ├── transform() ──→ Pydantic validation + normalization
            └── load() ────────→ PostgreSQL
                    ├── upserts ── books
                    ├── updates ── scrape_state  (advance watermark)
                    └── records ── pipeline_runs (audit log)
```

---

## Sample Data

**`books` table**

| title | rating | price | category | availability |
|---|---|---|---|---|
| A Light in the Attic | 3 | 51.77 | Poetry | In stock |
| Tipping the Velvet | 1 | 53.74 | Historical Fiction | In stock |
| Soumission | 1 | 50.10 | Fiction | In stock |

**`pipeline_runs` table**

| started_at | completed_at | status | rows_extracted | rows_loaded | rows_skipped |
|---|---|---|---|---|---|
| 2026-05-01 10:00:00 | 2026-05-01 10:04:32 | success | 1000 | 1000 | 0 |

---

## Quick Start (Docker)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
cp .env.example .env
docker compose up
```

The scraper waits for Postgres to pass its healthcheck before starting. Scraped data persists in a Docker volume across restarts.

---

## Local Setup

**Requirements:** Python 3.11+, PostgreSQL 16+

```bash
# 1. Clone and create a virtual environment
git clone https://github.com/CameronLewis08/Online-Ecommerce-Scraper.git
cd Online-Ecommerce-Scraper
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Postgres credentials

# 4. Start the pipeline
python scheduler.py
```

---

## Configuration

All configuration is read from `.env` (copy `.env.example` to get started):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `SCRAPE_INTERVAL_MINUTES` | `60` | How often the pipeline runs |
| `REQUEST_DELAY_SECONDS` | `1.0` | Delay between page requests |
| `LOG_FILE` | `logs/pipeline.log` | Log file path |
| `LOG_MAX_BYTES` | `5242880` | Max log size before rotation (5 MB) |
| `LOG_BACKUP_COUNT` | `3` | Number of rotated log files to keep |

---

## Running Tests

```bash
pytest
```

---

## Project Structure

```
├── config/
│   └── settings.py         # env-based configuration
├── db/
│   ├── connection.py        # SQLAlchemy engine and session factory
│   └── models.py            # ORM models: Book, PipelineRun, ScrapeState
├── scraper/
│   ├── extract.py           # HTTP scraping with pagination and resume logic
│   ├── transform.py         # Pydantic validation and field normalization
│   ├── load.py              # Upsert + scrape_state watermark update
│   └── pipeline.py          # Orchestration and logging setup
├── tests/
│   ├── test_transform.py
│   └── test_load.py
├── logs/                    # Rotating log output (gitignored)
├── scheduler.py             # APScheduler entry point
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Contact

GitHub: [CameronLewis08](https://github.com/CameronLewis08)
