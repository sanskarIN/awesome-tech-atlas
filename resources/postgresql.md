# PostgreSQL documentation

**Official source:** https://www.postgresql.org/docs/current/  
**Type:** official docs  
**Category:** [Databases & storage systems](../categories/databases-storage.md) · Client-server relational database  
**Last official-page inspection:** 2026-11-08

## Why it matters

Official PostgreSQL reference for SQL, data types, transactions, administration, and extension features.

## Good fit

Applications needing a managed relational database server and concurrent clients.

## Strength and trade-off

- **Strength:** Extensive SQL and administration reference helps with production database design.
- **Limitation:** A database server adds operational work: backups, security configuration, monitoring, and upgrades.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

On a local test installation, connect using `psql` and run `SELECT current_database();`.

## Worked example: roll back part of a local transaction

### Prerequisites

- A running **non-production** PostgreSQL instance, a test database you may connect to, and the `psql` command-line client.
- Permission to create temporary tables. Save this original sample as `atlas_transaction.sql`. It is designed for a disposable database session, not a real application schema.

### Steps

Run `psql -X -v ON_ERROR_STOP=1 -d YOUR_TEST_DATABASE -f atlas_transaction.sql`, replacing the database name with your own test database. The script creates a session-local temporary table, inserts one row, then undoes a second insert using a savepoint.

~~~sql
BEGIN;
CREATE TEMP TABLE atlas_tasks (
  id integer PRIMARY KEY,
  title text NOT NULL
);
INSERT INTO atlas_tasks (id, title) VALUES (1, 'keep');
SAVEPOINT after_first_insert;
INSERT INTO atlas_tasks (id, title) VALUES (2, 'undo');
ROLLBACK TO SAVEPOINT after_first_insert;
SELECT id, title FROM atlas_tasks ORDER BY id;
COMMIT;
~~~

`ROLLBACK TO SAVEPOINT` undoes the second insert without rolling back the earlier insert in the same transaction. The temporary table is scoped to the database session rather than being a permanent application table.

### Expected result

The `SELECT` returns **one row**, with `id` equal to `1` and `title` equal to `keep`. A row for `undo` should not appear. Extra command-status lines and table formatting depend on the `psql` version and settings.

### Troubleshooting

- If connection fails, check that PostgreSQL is running and that you are using an authorized **test** database and valid local credentials.
- If permission to create temporary tables is denied, ask the test database administrator; do not escalate permissions or use a production account.
- `ON_ERROR_STOP=1` makes a script stop when an SQL error occurs, but a failed script may still need its transaction state checked. This demo does not cover concurrent transactions or production error handling.

### Evidence and execution status

- **Primary references:** [PostgreSQL transaction tutorial](https://www.postgresql.org/docs/current/tutorial-transactions.html) and [savepoint reference](https://www.postgresql.org/docs/current/sql-savepoint.html).
- **Reviewed:** 2026-11-13 (example-specific official documentation). **Not runtime-tested here:** a PostgreSQL server and `psql` were unavailable in the verification environment.
- Expected results follow the documented transaction and savepoint semantics, but must be confirmed on a local test installation. The catalog's earlier inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://www.postgresql.org/docs/current/) for setup, compatible versions, and API details.
- **Alternative:** [SQLite documentation](sqlite.md). SQLite has a simpler embedded deployment model for many local applications.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
