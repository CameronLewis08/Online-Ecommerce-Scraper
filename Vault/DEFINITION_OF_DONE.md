# Definition of Done — E-Commerce ETL Pipeline

A phase is "done" when every checkbox is checked AND you can answer the interview
questions for that section without looking at the code. The questions are the kind
an interviewer will ask to test whether you understand what you built.

---

## Phase 1 — Project Setup

### Completion Criteria
- [ ] Virtual environment is active and isolated from system Python
- [ ] `requirements.txt` has pinned versions (e.g. `requests==2.31.0`, not `requests>=2`)
- [ ] `.env` exists locally but is not tracked by git
- [ ] `.env.example` is committed with placeholder values
- [ ] Application connects to Postgres successfully

### Interview Questions

**Q: Why use a virtual environment instead of installing packages globally?**
A: Global installs create version conflicts between projects. A virtual environment gives
each project its own isolated dependency tree. This also means `requirements.txt` only
contains what this project actually needs, not everything on the machine.

**Q: Why pin exact versions in requirements.txt?**
A: Unpinned dependencies (`requests>=2`) can silently upgrade to a breaking version
in a new environment. Pinned versions (`requests==2.31.0`) guarantee the same behavior
everywhere — on your machine, a teammate's machine, or a CI runner.

**Q: Why should `.env` never be committed to git?**
A: `.env` contains credentials. Once committed, they exist in git history forever — even
after deletion. Anyone with access to the repo can read them. Credentials that are
accidentally committed must be rotated immediately.

---

## Phase 2 — Database Layer

### Completion Criteria
- [ ] All three tables exist in Postgres with correct column types
- [ ] `books.url` has a UNIQUE constraint
- [ ] Running the table creation script twice does not produce errors
- [ ] Connection is managed through a single engine/session factory
- [ ] No database credentials appear anywhere except `config/settings.py`

### Interview Questions

**Q: Why use SQLAlchemy instead of writing raw SQL?**
A: SQLAlchemy parameterizes queries automatically, eliminating SQL injection risk. It also
manages connection pooling, handles database dialect differences, and lets you define your
schema as Python classes — which are easier to version control and refactor than SQL strings.

**Q: What is connection pooling and why does it matter?**
A: Opening a new database connection is expensive (authentication, TCP handshake). A
connection pool keeps a set of connections open and reuses them. Without pooling, a pipeline
that makes thousands of queries would be slow and could exhaust the database's connection limit.

**Q: Why does `books.url` need a UNIQUE constraint?**
A: The upsert logic relies on it. `INSERT ... ON CONFLICT (url) DO UPDATE` can only detect
a conflict if Postgres knows the column must be unique. Without the constraint, the same
book could be inserted multiple times as duplicates.

**Q: Why do you have a `scrape_state` table?**
A: It stores the watermark — the last page successfully scraped. On the next run, the
scraper reads this value and starts from there instead of page 1. Without it, every run
would re-process all data, which is inefficient and not incremental.

**Q: What is idempotency in the context of a pipeline?**
A: An idempotent operation produces the same result no matter how many times you run it.
For this pipeline: running it twice on the same data should result in the same rows in the
database — not doubled rows. Upsert logic is what makes the load step idempotent.

---

## Phase 3 — Extract

### Completion Criteria
- [ ] Scraper handles pagination without manual intervention
- [ ] Scraper resumes from the last scraped page on restart
- [ ] A delay exists between page requests
- [ ] A descriptive User-Agent header is set on the session
- [ ] Each page scraped produces an INFO log entry

### Interview Questions

**Q: What is BeautifulSoup and what does it do?**
A: BeautifulSoup is a Python library that parses HTML into a navigable tree structure.
You pass it raw HTML from an HTTP response, and it lets you search for elements by tag
name, CSS class, ID, or attribute — similar to how a browser's DevTools inspector works.

**Q: Why add a time.sleep() between requests?**
A: Without delays, the scraper would send hundreds of requests per second. This can
overload the server, trigger rate limiting or IP bans, and is considered hostile behavior.
A delay of 1–3 seconds mimics human browsing and is an ethical scraping baseline.

**Q: What is robots.txt and why does it matter?**
A: robots.txt is a file at the root of a website that declares which paths automated
agents are allowed to access. Ignoring it is both unethical and, in some jurisdictions,
potentially a legal issue. Always check it before scraping a new site.

**Q: What is incremental loading and how did you implement it?**
A: Incremental loading means only processing new data, not re-processing everything from
scratch. I implemented it with a `scrape_state` table that stores the last page scraped.
On each run, the extractor reads this value and starts pagination from that page.

---

## Phase 4 — Transform

### Completion Criteria
- [ ] Every field passes through Pydantic validation before proceeding
- [ ] Rating words ("One" through "Five") are converted to integers 1–5
- [ ] Price is a Decimal with the currency symbol stripped
- [ ] Validation failures are logged as WARNINGs and counted — never raise an exception
- [ ] The transform function returns both valid models and a skipped-row count

### Interview Questions

**Q: What is Pydantic and why use it for validation?**
A: Pydantic is a Python library that uses type annotations to validate and coerce data at
runtime. You define a model class with typed fields, and Pydantic raises a `ValidationError`
if the data doesn't match. It's faster than writing manual validation, produces clear error
messages, and integrates well with type checkers.

**Q: Why is the Transform step separate from Extract?**
A: Separation of concerns. The extractor's job is to get data from the source — it should
not care about types or business rules. The transformer's job is to clean and validate — it
should not care about HTTP or HTML parsing. This makes each step testable in isolation and
replaceable independently.

**Q: What happens when a row fails validation in your pipeline?**
A: The ValidationError is caught per row, a WARNING is logged with the row content and
error reason, the row is counted as `rows_skipped`, and the pipeline continues to the next
row. The pipeline does not crash. At the end, `rows_skipped` is written to `pipeline_runs`
so you have a record of how many rows were lost and why.

**Q: Why store price as Decimal rather than float?**
A: Floats use binary representation and have rounding errors — `0.1 + 0.2` in a float is
`0.30000000000000004`. For monetary values, this is unacceptable. `Decimal` stores numbers
exactly as entered and rounds predictably, which is why financial systems always use it.

---

## Phase 5 — Load

### Completion Criteria
- [ ] Loading the same data twice produces no duplicate rows
- [ ] All rows in a batch are wrapped in a single transaction
- [ ] `scrape_state` is updated after every successful load
- [ ] A failed batch rolls back — no partial state in the database

### Interview Questions

**Q: What is an upsert and how does it work in PostgreSQL?**
A: An upsert is an INSERT that handles conflicts. The syntax is:
`INSERT INTO books (...) VALUES (...) ON CONFLICT (url) DO UPDATE SET ...`
If a row with that URL already exists, Postgres updates it in place instead of inserting
a duplicate. This makes the operation idempotent — safe to run multiple times.

**Q: Why wrap batch inserts in a transaction?**
A: If loading 100 rows and row 67 fails, a transaction ensures rows 1–66 are rolled back.
Without a transaction, you'd have a partial load — 66 rows in the database with 34 missing,
and no way to know which. Transactions give you "all or nothing" semantics.

**Q: What is the difference between INSERT and UPSERT?**
A: INSERT always tries to create a new row. If a row with a conflicting unique key exists,
it raises an error. UPSERT handles the conflict by either ignoring the duplicate or updating
the existing row — the behavior you specify. For a scraper that re-encounters the same books
across runs, upsert is the correct choice.

**Q: Why does the load step update scrape_state?**
A: The load step is the final confirmation that data made it to the database. Updating the
watermark here, not in the extract step, means if the load fails, the state does not advance.
On the next run, the extractor will re-scrape those pages and try again.

---

## Phase 6 — Pipeline Orchestration

### Completion Criteria
- [ ] `pipeline_runs` has one row per run with correct start/end times and counts
- [ ] A pipeline failure sets `status='failed'` with a non-null `error_message`
- [ ] All output goes through the Python logger — no `print()` statements anywhere
- [ ] Log output appears in both the console and `logs/pipeline.log`
- [ ] The log file uses a `RotatingFileHandler` with a size limit

### Interview Questions

**Q: Why log to both stdout and a file?**
A: Stdout provides real-time visibility when running locally or watching a container.
File logs persist after the process exits, so you can review what happened after a failure.
In production these would both be aggregated into a logging platform like Datadog or Splunk.

**Q: What is the purpose of the pipeline_runs table?**
A: It is the pipeline's audit log and monitoring surface. It answers: Did the pipeline run?
Did it succeed? How much data did it process? How long did it take? Is it getting slower?
Without it, you have no visibility into pipeline health over time.

**Q: What is a RotatingFileHandler and why use it?**
A: It is a log handler that starts a new log file after the current one reaches a size limit
(e.g. 5 MB), keeping a configurable number of old files. Without it, a long-running pipeline
produces a single log file that grows until it fills the disk.

**Q: How does your pipeline handle an unexpected exception?**
A: The `pipeline.run()` function wraps the entire E→T→L sequence in a try/except. If any
unhandled exception escapes, the except block catches it, logs the traceback at ERROR level,
and updates the `pipeline_runs` row with `status='failed'` and the exception message. The
pipeline shuts down cleanly instead of leaving a run in `status='running'` forever.

---

## Phase 7 — Scheduler

### Completion Criteria
- [ ] The scheduler runs the pipeline on a configurable interval
- [ ] The interval is set via `.env`, not hardcoded
- [ ] `pipeline_runs` accumulates one new row per scheduled execution
- [ ] The scheduler logs when it starts and when each job fires

### Interview Questions

**Q: What is APScheduler and why use it instead of a cron job?**
A: APScheduler is a Python library for scheduling jobs within a running process. Unlike
cron, it doesn't require OS-level configuration, it's cross-platform, and it keeps the
schedule inside the project — visible in code, version controlled, and portable.

**Q: What is the difference between a script and a pipeline?**
A: A script is a one-off program you run manually. A pipeline is a scheduled, repeatable
process that runs automatically, handles its own errors, and produces observable output.
The scheduler is what promotes this project from a script to a pipeline.

**Q: Why make the interval configurable via .env?**
A: Different environments need different intervals. Development might use 1 minute for
quick testing; production might use 1 hour. Hardcoding the interval would require a code
change (and a redeployment) to adjust it. An environment variable means you change the
config, not the code.

---

## Phase 8 — Testing

### Completion Criteria
- [ ] All transform normalization logic has unit test coverage
- [ ] The upsert behavior is tested — same URL, no duplicate
- [ ] All tests pass with `pytest`
- [ ] HTTP calls are mocked in extractor tests (the live site is not hit)

### Interview Questions

**Q: Why is transform.py the easiest module to unit test?**
A: Transform functions are pure — they take input and return output with no side effects,
no database calls, no network calls. You can test them with simple assertions: given this
dict, expect this Pydantic model. No mocking, no setup, no teardown required.

**Q: How do you test code that makes HTTP requests without hitting the live site?**
A: Mock the `requests.get()` call to return a pre-defined HTML response fixture. Libraries
like `unittest.mock.patch` or `responses` let you intercept outgoing HTTP calls and return
whatever you specify. Tests that hit live sites are slow, flaky, and depend on external state.

**Q: What is the value of testing upsert logic?**
A: Upsert is the mechanism that ensures idempotency. If it breaks (e.g. someone changes
the conflict target), the pipeline starts creating duplicates silently. A test that loads
the same row twice and asserts `COUNT(*) == 1` catches this regression immediately.

---

## Phase 9 — Docker (Optional)

### Completion Criteria
- [ ] `docker compose up` runs the full pipeline with no manual setup steps
- [ ] Postgres data persists across container restarts (volume mounted)
- [ ] The scraper does not start until Postgres is ready (`depends_on` with healthcheck)

### Interview Questions

**Q: What problem does Docker solve for this project?**
A: It eliminates the "works on my machine" problem. Docker packages the application and its
runtime environment together. Anyone with Docker installed can run `docker compose up` and
get an identical, working environment — regardless of their OS or Python version.

**Q: What is a Docker volume and why do you need one for Postgres?**
A: Container filesystems are ephemeral — data written inside a container is lost when the
container stops. A volume mounts a directory from the host machine into the container, so
Postgres data persists across restarts. Without a volume, the database is empty every time.

**Q: What does `depends_on` with a healthcheck do in docker-compose.yml?**
A: `depends_on` alone only waits for the container to start, not for the service inside
to be ready. Adding a healthcheck (a command that returns success when Postgres is accepting
connections) ensures the scraper does not attempt to connect before the database is ready.
This prevents a race condition on startup.
