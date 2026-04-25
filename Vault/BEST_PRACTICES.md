# Engineering Best Practices — E-Commerce ETL Pipeline

A reference document for industry standards applied in this project.
Consult this when making design decisions or preparing for interviews.

---

## 1. ETL Pipeline Design

**Idempotency**
A pipeline run should be safe to run multiple times and always produce the same result.
If the scraper runs twice on the same data, the database should not have duplicates.
This is achieved through upsert logic (INSERT ... ON CONFLICT DO UPDATE).

**Incremental Loading**
Never re-process data you have already processed. Use a watermark — a stored pointer
to where you last left off (last page scraped, last timestamp) — so each run picks up
where the previous one ended. This is stored in the `scrape_state` table.

**Separation of Concerns**
Extract, Transform, and Load are three distinct responsibilities. Each should be its
own module with its own function. This makes each step independently testable and
replaceable without touching the others.

**Atomic Operations**
Multi-row database writes should happen inside a transaction. If loading 50 rows and
row 30 fails, the entire batch should roll back — not leave 29 rows in a partial state.

**Fail Loudly**
Pipelines should not silently swallow errors. A failed row should be logged with enough
context to debug. A failed run should update `pipeline_runs.status` to 'failed' with
an error message, not just exit with no trace.

---

## 2. Configuration Management

- All credentials and environment-specific values live in a `.env` file — never hardcoded
- `.env` is gitignored; `.env.example` (with placeholder values) is committed
- A central `config/settings.py` loads all env vars once using `python-dotenv`
- No file other than `settings.py` should ever call `os.getenv()` directly
- This means changing a config value requires changing exactly one place

---

## 3. Data Validation

**Validate at the boundary.**
Raw data from the web cannot be trusted. Validate every field before it enters the
database. Pydantic enforces types, required fields, and value constraints at parse time.

**Track failures, don't crash on them.**
A row that fails validation should be counted and logged, not crash the entire pipeline.
The `pipeline_runs` table records `rows_skipped` for exactly this reason.

**Be explicit about types.**
A rating of "Five" is not the same as a rating of 5. A price of "£12.99" is not a
decimal. Normalization (converting these to proper types) happens in the Transform step.

---

## 4. Database Best Practices

**Use an ORM (SQLAlchemy)**
Never construct SQL by string concatenation — this is the #1 cause of SQL injection.
SQLAlchemy parameterizes queries safely by default.

**Connection Pooling**
Don't open a new database connection for every query. SQLAlchemy manages a pool of
reusable connections automatically. Configure pool size based on workload.

**Upserts Over Inserts**
Use INSERT ... ON CONFLICT DO UPDATE (PostgreSQL's upsert syntax) instead of checking
for existence before inserting. It is atomic, faster, and correct under concurrency.

**Index What You Query**
Add indexes on columns used in WHERE clauses, JOIN conditions, or ORDER BY.
For this project: `books.url` (unique constraint implies an index) and
`pipeline_runs.started_at` for time-based queries.

**Use Transactions**
Wrap batch inserts in a transaction so partial failures roll back cleanly.

---

## 5. Logging

**Use the `logging` module, never `print()`**
Print statements disappear in production. Loggers write to files, support log levels,
and can be routed to monitoring systems.

**Log levels matter**
- DEBUG: detailed step-by-step info (only visible in dev)
- INFO: normal milestones ("Scraped page 3 of 50", "Loaded 47 rows")
- WARNING: something unexpected but recoverable ("Row skipped: missing price")
- ERROR: something failed ("Database connection refused")

**Include context**
"Loaded rows" is a bad log message. "Loaded 47/50 rows, 3 skipped (validation error)" is good.

**Log to both stdout and a rotating file**
Stdout is for real-time visibility. File logs are for debugging after the fact.
Use `RotatingFileHandler` to prevent log files from growing indefinitely.

---

## 6. Error Handling

**Distinguish transient from permanent failures**
- Transient: network timeout, temporary DB unavailability → retry with backoff
- Permanent: malformed HTML structure, missing field → log and skip the row

**Exponential Backoff for Retries**
Don't retry immediately — wait, then wait longer. This prevents hammering a server
that is already struggling. Pattern: wait 1s, then 2s, then 4s before giving up.

**Never use bare `except:`**
Always catch specific exception types. `except Exception as e:` is acceptable.
`except:` swallows keyboard interrupts and system exits — it is always wrong.

---

## 7. Ethical Scraping

**Check robots.txt first**
Before scraping any site, read its robots.txt file (at site.com/robots.txt).
It declares what paths scrapers are and are not allowed to access. Respect it.

**Set a descriptive User-Agent**
Identify your scraper honestly: `"EcommerceETL-Portfolio/1.0 (educational project)"`.
Anonymous or deceptive user agents are considered hostile.

**Rate Limit Your Requests**
Add a `time.sleep()` between requests. A real scraper adds 1–3 seconds of delay.
This prevents overloading the server and gets you blocked less often.

**Scrape Only What You Need**
Don't scrape fields you have no use for. Don't scrape more pages than necessary.

**books.toscrape.com** is designed specifically for scraping practice — no ToS concerns.

---

## 8. Project Structure

A well-structured Python project is not one giant script. It is a package with clear
separation of responsibilities. Each module does one thing and does it well.

```
ecommerce-etl/
├── config/         # Configuration only — no business logic
├── db/             # Database models and connection — no scraping logic
├── scraper/        # ETL logic — no config or DB schema concerns
├── tests/          # Tests only — mirrors scraper/ structure
└── logs/           # Log output — never committed to git
```

**Why this matters:** If someone asks you to swap PostgreSQL for MySQL, you should only
need to touch `db/`. If someone asks you to scrape a different site, you only touch
`scraper/extract.py`. Tight coupling means a change in one place breaks something else.

---

## 9. Testing

**What to test in this project**
- `transform.py` — pure functions, easy to unit test with no dependencies
- `load.py` — test upsert logic against a test database or with mocked sessions
- `pipeline.py` — integration test: run the full pipeline against fixture data

**What not to over-test**
The extractor makes HTTP calls. Mock the HTTP layer in tests (use `unittest.mock`
or the `responses` library) — don't hit the live site in your test suite.

**Tests as documentation**
A test named `test_rating_word_converts_to_int` tells the next developer exactly
what the transform is supposed to do. Good test names are better than comments.

---

## 10. Observability

**The pipeline_runs table IS your monitoring system**
Every run should produce one row: when it started, when it ended, how many rows
were processed, how many failed, and whether it succeeded. This lets you answer:
- Is the pipeline running?
- Is it getting slower over time?
- How often does it fail, and why?

This is the data engineering equivalent of application metrics. In production this
would feed into a dashboard (Grafana, DataDog). Here, it feeds into your interview story.
