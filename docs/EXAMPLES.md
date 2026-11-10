# Hands-on examples

These original walkthroughs are attached to reviewed resource profiles. Each has prerequisites, a concrete task, an expected outcome, troubleshooting, and specific upstream references. Examples are intentionally small: they **teach one concept**, not production readiness.

| Area | Walkthrough | What it demonstrates |
| --- | --- | --- |
| Programming | [Python: summarize CSV status](../resources/python.md#worked-example-summarize-a-tiny-csv-dataset) | Parse rows and count statuses using only the standard library |
| Data and ML | [scikit-learn: train/test split](../resources/scikit-learn.md#worked-example-classify-flowers-without-preprocessing-leakage) | Use a training-only preprocessing pipeline and examine output dimensions |
| Systems | [Rust: count log warnings](../resources/rust.md#worked-example-count-warning-lines-in-a-local-log) | Read a text file and report counts with standard library functions |
| Web UI | [React: stateful checklist](../resources/react.md#worked-example-an-accessible-stateful-checklist) | Update local UI state from an accessible checkbox |
| Security | [OWASP: default-deny policy tests](../resources/owasp-cheatsheets.md#worked-example-test-a-default-deny-authorization-rule) | Exercise a *toy* authorization rule with local unit tests |
| Storage | [SQLite: bound parameters](../resources/sqlite.md#worked-example-query-a-local-task-list-with-bound-parameters) | Query a transient database without constructing SQL from input strings |
| Scientific computing | [NumPy: center readings](../resources/numpy.md#worked-example-center-sensor-readings-by-column) | Compute column means and apply array broadcasting |

## What was actually verified?

Each linked profile separately records its example-specific review date and distinguishes **executed locally** from **not runtime-tested**. Do not treat a reviewed example as proof of compatibility with every supported platform, operating system, dependency version, or deployed application. The latest SQLite and NumPy walkthroughs were run with the versions stated in their profiles.

Automated checks in `tests/test_worked_examples.py` ensure that these Markdown walkthroughs keep their structure and that their embedded Python examples **parse**. CI deliberately does **not execute** snippets extracted from contributed Markdown, and Rust/React samples require manual runtime and real-browser review.

## Run in a local checkout

Use the exact commands in the profile you select. Follow the prerequisites first; most examples use local data and do not need an external service. To read all profiles without a network connection, see [the single-file offline explorer](EXPLORE.md#option-c-build-a-fully-offline-searchable-html-file).

Found an error or a missing limitation? Follow [the contribution guide](../CONTRIBUTING.md) and open a correction with the environment, observed output, and authoritative source.
