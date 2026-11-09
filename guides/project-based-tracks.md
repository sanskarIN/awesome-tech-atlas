# Project-based learning tracks

These projects turn curated references into **small, inspectable artifacts**. Start with a track that fits your skill level, work entirely with sample or non-sensitive data, and change the scope to suit your available tools. A passing toy example is not proof of production readiness.

Each track names prerequisites, an incremental plan, a definition of done, evidence to retain, and a sensible stretch goal. For minimal examples to try first, consult the linked resource profiles.

## Track 1: Python command-line data summary

**Goal:** Create a small program that summarizes non-sensitive CSV records and fails clearly on malformed input.

**Suggested background:** [Python](../resources/python.md), [Git](../resources/git.md), and [The Missing Semester](../resources/missing-semester.md).

**Prerequisites:** Python 3.10+; a text editor and Git. The first implementation can use only Python's standard library.

1. Start with the [in-memory CSV example](../resources/python.md#worked-example-summarize-a-tiny-csv-dataset); reproduce its expected counts.
2. Move the sample input into a small `sample.csv` file that you created. Add a command-line path parameter and show a clear usage message when the argument is missing.
3. Separate parsing from reporting into named functions; count only nonempty, known status values, and explicitly report invalid rows instead of silently discarding them.
4. Add automated tests for a valid file, empty input, an unexpected column name, and an unknown status. Keep test fixtures small.
5. Document `python -m unittest` (or your chosen test command), example input/output, supported Python version, and known limitations.

**Definition of done:** another learner can clone the project, run its documented command, reproduce the expected counts, and observe all four edge-case tests pass.

**Evidence to retain:** your test output, a short README, and one PR or commit explaining why you changed the input handling.

**Watch for:** file encoding, spreadsheet CSV dialects, untrusted file paths, and assumptions about column headers. The example is not a general-purpose CSV validation product.

**Stretch:** add a `--help` message and make output ordering deterministic, without adding a dependency merely for convenience.

## Track 2: Reproducible classical ML experiment

**Goal:** Train and evaluate a small classifier while preventing preprocessing from learning from held-out test examples.

**Suggested background:** [Python](../resources/python.md), [NumPy](../resources/numpy.md), and [scikit-learn](../resources/scikit-learn.md).

**Prerequisites:** a compatible Python environment with scikit-learn installed according to its [upstream setup guidance](https://scikit-learn.org/stable/install.html). No personal or proprietary dataset is needed.

1. Reproduce the [Iris classification example](../resources/scikit-learn.md#worked-example-classify-flowers-without-preprocessing-leakage).
2. Explain the role of the seeded `train_test_split` and why `StandardScaler` belongs inside a fitted pipeline.
3. Record the training/test row counts, a confusion matrix, and the installed Python and scikit-learn versions. Do not present toy-dataset accuracy as a real-world claim.
4. Write a second experiment using a different supported estimator **on the same split**. Record the comparison protocol before interpreting any results.
5. Explain the remaining risks: tiny sample size, data leakage from target-related features, and how results can change when the population differs.

**Definition of done:** a clean environment can rerun the experiment, produce the stated dataset sizes and diagnostic report, and verify that no preprocessing step was fitted on the test records.

**Evidence to retain:** a dependency list or reproducible environment specification, the script, evaluation output, and a limitations section.

**Watch for:** evaluating repeatedly on a test set during model selection, leakage through preprocessing, and treating class labels as claims about real people.

**Stretch:** add a cross-validation experiment on the training partition only, while preserving an untouched final test partition.

## Track 3: Accessible web checklist

**Goal:** Build a small interaction whose state changes predictably and which can be operated without a mouse.

**Suggested background:** [MDN Learn](../resources/mdn-learn.md), [MDN JavaScript](../resources/javascript-mdn.md), and [React Learn](../resources/react.md).

**Prerequisites:** an existing React project that supports JSX, or first complete the relevant MDN HTML/JavaScript modules.

1. Reproduce the [React checklist](../resources/react.md#worked-example-an-accessible-stateful-checklist).
2. Add two more example tasks with stable IDs and descriptive labels. Keep them in memory, not on a remote service.
3. Verify that checking/unchecking a task changes only its intended record and updates the completion summary.
4. Operate every checkbox using a keyboard and check the focus indicator and label relationship. Test in a browser with an assistive technology workflow when possible; an `aria-live` attribute alone is not an accessibility audit.
5. Document how the application behaves on refresh and what state you chose **not** to persist.

**Definition of done:** tasks are operable using keyboard input, the count stays consistent after multiple toggles, the code does not mutate React state in place, and the README explains the reset-on-reload behavior.

**Evidence to retain:** a manual test checklist, browser/tool versions, and the exact accessibility checks performed.

**Watch for:** missing labels, duplicate React keys, focus visibility, and assuming a static example covers routing, authentication, privacy, or persistence.

**Stretch:** compare the same checklist implemented with browser DOM APIs. Explain the extra setup and abstractions each approach requires without declaring a universal winner.

## Track 4: Rust local log inspector

**Goal:** Read a local test log, count warning lines, and provide sensible errors for invalid input.

**Suggested background:** [The Rust Programming Language](../resources/rust.md), [Git](../resources/git.md), and optional [Linux kernel docs](../resources/linux-kernel-docs.md) for broader systems context.

**Prerequisites:** a supported Rust toolchain with Cargo. Use synthetic text logs, not application logs containing passwords or personal records.

1. Reproduce the [Rust counting example](../resources/rust.md#worked-example-count-warning-lines-in-a-local-log).
2. Extend the program to show a helpful usage message and a useful error when a file cannot be read.
3. Move the counting logic into a function that accepts `&str` so it can be unit-tested without touching the filesystem.
4. Add tests for empty input, mixed levels, and a warning prefix inside a non-warning line.
5. Use `cargo fmt`, `cargo test`, and `cargo clippy` if those components are available, then write down the actual checks you ran.

**Definition of done:** the documented example input produces the expected count, malformed or missing inputs do not produce misleading success, and the pure counting function has meaningful tests.

**Evidence to retain:** Cargo version, test output, sample input, and the source commit used for verification.

**Watch for:** assumptions about UTF-8, case sensitivity, line endings, and logs that do not conform to your toy syntax. Do not confuse prefix matching with a full parser.

**Stretch:** compare the maintainability of this small native tool with an equivalent Python script; make any speed claim only after designing a repeatable benchmark.

## Track 5: Maintain a small open-source knowledge entry

**Goal:** Propose one evidence-backed improvement through the project's normal contribution process.

**Suggested background:** [Open Source Guides](../resources/open-source-guides.md), [Git](../resources/git.md), and [GitHub Actions](../resources/github-actions.md).

**Prerequisites:** a GitHub account and a topic branch on a repository you are authorized to contribute to. You may practice on a local copy without publishing.

1. Read the [editorial policy](../docs/EDITORIAL_POLICY.md) and the [resource template](../docs/RESOURCE_TEMPLATE.md).
2. Choose an existing profile whose troubleshooting or practical first step can be improved. Check its upstream source before editing.
3. Make one focused, original documentation change. Clearly mark what was tested versus documentation-reviewed.
4. Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`; inspect errors instead of bypassing the checks.
5. Open a pull request with the evidence and limitations. Follow [branch-protection guidance](../docs/BRANCH_PROTECTION.md) before merge.

**Definition of done:** the patch is understandable without screenshots, internal navigation remains valid, and the PR explains exactly which sources and tests support it. A reviewer may still ask for changes.

**Evidence to retain:** the reviewed official URLs, local test output, and the PR's explanation. Never publish authentication tokens, third-party secrets, or private user data.

**Stretch:** propose a focused editorial issue for a genuine coverage gap with a clear inclusion rationale, rather than importing an unchecked list of links.

---

## A reusable project evidence card

For any track, keep a short Markdown record like this:

| Item | What to record |
| --- | --- |
| Purpose | One sentence about the learner-visible outcome |
| Environment | OS, runtime/tool versions, key dependencies |
| Inputs | Whether records are synthetic, public, or otherwise authorized |
| Reproduction | Commands to install, build, run, and test |
| Observations | Exact output or interaction actually seen |
| Known limitations | Untested platforms, edge cases, and scope exclusions |
| Next investigation | One question that justifies further work |

A completed project card is better than an unsupported claim that a tool is *production-ready*. The [decision worksheet](decision-worksheet.md) can help choose between multiple viable approaches.
