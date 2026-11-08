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

## Where to go next

- Read the [upstream documentation](https://www.postgresql.org/docs/current/) for setup, compatible versions, and API details.
- **Alternative:** [SQLite documentation](sqlite.md). SQLite has a simpler embedded deployment model for many local applications.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
