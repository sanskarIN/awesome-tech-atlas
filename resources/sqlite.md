# SQLite documentation

**Official source:** https://www.sqlite.org/docs.html  
**Type:** official docs  
**Category:** [Databases & storage systems](../categories/databases-storage.md) · Embedded relational database  
**Last official-page inspection:** 2026-11-08

## Why it matters

Upstream documentation for the embeddable SQLite database, SQL syntax, CLI, and interfaces.

## Good fit

Local storage, prototypes, desktop apps, and deployments that benefit from a database file.

## Strength and trade-off

- **Strength:** No standalone DB server is required for common embedded use cases.
- **Limitation:** Concurrent access patterns, filesystem behavior, and server-style needs deserve special attention.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

With Python installed, open `sqlite3.connect(':memory:')` in a small practice script.

## Worked example: query a local task list with bound parameters

### Prerequisites

- Python 3.10 or later (the standard-library `sqlite3` module; no separate database server).
- Save the original program as `tasks_sqlite.py`. It uses an in-memory database, so no file is created or persisted.

### Steps

Run `python tasks_sqlite.py` (or `python3 tasks_sqlite.py` if that is your Python command):

~~~python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect(":memory:")) as connection:
    connection.execute(
        "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
        "done INTEGER NOT NULL CHECK (done IN (0, 1)))"
    )
    connection.executemany(
        "INSERT INTO tasks (title, done) VALUES (:title, :done)",
        [
            {"title": "Read docs", "done": 1},
            {"title": "Test query", "done": 0},
            {"title": "Write notes", "done": 1},
        ],
    )
    pending = connection.execute(
        "SELECT title FROM tasks WHERE done = :done ORDER BY id", {"done": 0}
    ).fetchall()
    completed = connection.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = :done", {"done": 1}
    ).fetchone()[0]
    print("pending:", ", ".join(row[0] for row in pending))
    print("completed:", completed)
~~~

The `:done` and `:title` placeholders bind **values** separately from SQL syntax. Avoid constructing SQL with interpolated user input. The `closing` context manager closes the database connection when finished.

### Expected result

~~~text
pending: Test query
completed: 2
~~~

### Troubleshooting

- If `sqlite3` is unavailable, check whether the Python installation includes that optional standard-library extension.
- `":memory:"` databases disappear when the connection is closed; switch to a named local file only if persistence is intended.
- Bind values rather than concatenating strings; placeholders cannot replace SQL identifiers such as table names. This example is single-process and does not test concurrent writes or durability.

### Evidence and execution status

- **Primary references:** [Python `sqlite3` documentation](https://docs.python.org/3/library/sqlite3.html) (parameter substitution and connection use) and [SQLite expression parameters](https://www.sqlite.org/lang_expr.html#varparam).
- **Reviewed:** 2026-11-10 (example-specific documentation). **Executed locally:** Python 3.13.5 with SQLite 3.46.1; output matched the two lines shown above.
- This local toy example does not establish production storage durability, concurrency behavior, or application security. The catalog's original official-page inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://www.sqlite.org/docs.html) for setup, compatible versions, and API details.
- **Alternative:** [PostgreSQL documentation](postgresql.md). PostgreSQL suits centralized server deployments and different concurrency needs.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
