# Main branch protection and recovery

This document records the repository's live **Protect main** ruleset as inspected on **2026-11-09**. It is a maintenance snapshot, not a substitute for [GitHub's current ruleset settings](https://github.com/sanskarIN/awesome-tech-atlas/settings/rules).

## Enforced settings at the time of inspection

| Rule | Current behavior |
| --- | --- |
| Target | The repository default branch (`main`) |
| Enforcement | Active |
| Entry path | Pull request required |
| Approving reviews | **0 required** (solo-maintainer configuration; independent review still welcome) |
| Review threads | Must be resolved before merge |
| CI | `Catalog, Markdown, and tests` required |
| Up-to-date checks | Required: the PR branch must satisfy strict required status checks |
| History | Non-fast-forward updates prohibited (no force pushes) |
| Deletion | Protected branch deletion prohibited |
| Bypass actors | None configured |
| Allowed merge methods | Merge, squash, rebase |

The ruleset identifier at the time of inspection was `26784576`. Settings may change after this date. Do not claim that one approving review is mandatory unless the active settings actually enforce it.

## Normal contribution flow

1. Create a short-lived topic branch from the latest `main`.
2. Make a focused edit and run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v` locally.
3. Open a PR targeting `main`, explain the source evidence and any runtime checks not performed.
4. Let GitHub Actions finish. Confirm **Catalog, Markdown, and tests** passes for the current commit and that review threads are resolved.
5. Rebase or update the topic branch if GitHub reports that the strict check requires a newer base. Re-run checks.
6. Merge only after reviewing the diff and any unresolved uncertainties; delete the topic branch after successful merge.

Even though the ruleset permits merging with zero approving reviews, this is **not** an instruction to merge unchecked changes. Seek review when another trusted maintainer is available.

## If CI fails or a PR is blocked

- Open the failed run and inspect the first failing validation or test step.
- Fix the underlying code/content on the topic branch; do **not** force-push `main` or disable a check to hide a failure.
- For a flaky external upstream link, follow [maintenance triage](MAINTENANCE.md). The external-link audit is separate from the required content-validation check.
- For an outdated PR branch, update it from `main`, then wait for a fresh required check on the new head.
- If merge still fails, confirm the PR targets `main`, the exact required check name exists, and all review threads are resolved.

## Exceptional recovery (repository administrator)

Only when a verified critical fix cannot pass because the **protection mechanism itself** is broken:

1. Document the failure, affected PR/commit, and the least risky repair plan.
2. Prefer repairing the workflow on a topic branch with a passing replacement check and an auditable PR.
3. If a ruleset adjustment is genuinely unavoidable, an authorized administrator may temporarily edit it via **Settings → Rules → Rulesets → Protect main**. Record precisely what changed, why, and who approved it; do not remove protections for convenience.
4. Make the minimal fix, restore the original strict ruleset immediately, and verify that a subsequent test PR requires the expected checks.
5. Record the incident and update this document if the normal workflow changed.

There is no configured bypass actor. Do not assume that administrator access bypasses this ruleset automatically.

## Review cadence

Re-check these settings after adding maintainers, renaming CI jobs, changing the default branch, or modifying the repository's merge policy. With multiple available reviewers, reconsider whether one approval should become a mandatory rule.

Issue context: [#2 — Governance: protect main](https://github.com/sanskarIN/awesome-tech-atlas/issues/2).
