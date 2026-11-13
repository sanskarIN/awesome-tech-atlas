# GitHub Actions documentation

**Official source:** https://docs.github.com/en/actions  
**Type:** official docs  
**Category:** [Cloud computing & DevOps](../categories/cloud-computing-devops.md) · Continuous integration  
**Last official-page inspection:** 2026-11-08

## Why it matters

Official GitHub documentation for event-driven workflows, jobs, runners, and automation.

## Good fit

Validating repositories automatically on pull requests and after commits.

## Strength and trade-off

- **Strength:** Workflows live beside code and can automate tests and checks.
- **Limitation:** Workflow permissions, secrets, and third-party actions require careful review.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Read the quickstart, create a workflow that runs a safe local validation command on pull requests.

## Worked example: a read-only README check on pull requests

### Prerequisites

- A practice GitHub repository with a `README.md` file and permission to propose a workflow.
- Familiarity with YAML and pull requests. This sample is **not deployed** by reading this profile; save it as `.github/workflows/readme-check.yml` in your own practice repository.

### Steps

The following original workflow checks only that the checked-out README is nonempty and contains a Markdown heading:

~~~yaml
name: Check README
on:
  pull_request:

permissions:
  contents: read

jobs:
  readme:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
      - name: Inspect README
        run: |
          test -s README.md
          grep -Fq '# ' README.md
~~~

The `pull_request` event runs checks when a pull request is created or updated. The token is granted only `contents: read` for this basic job; it does not need write permission, secrets or a deployment key.

### Expected result

In the practice repository's pull-request checks, **Check README / readme** should pass for a nonempty README containing `# ` and fail when those conditions are absent. The sample intentionally does not deploy, publish, edit or upload anything.

### Troubleshooting

- If the workflow does not run, verify the path under `.github/workflows/` and whether GitHub Actions is enabled in the practice repository.
- If the README check fails, inspect the file at the pull request's checked-out revision. The command is intentionally simple: it is **not** a Markdown parser or proof of documentation quality.
- Workflow triggers and token permissions depend on repository settings and contribution origin. Review upstream action provenance; for stricter supply-chain controls, pin external actions to a vetted immutable commit SHA rather than only a moving major-version tag.

### Evidence and execution status

- **Primary references:** [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) and [automatic token permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication).
- **Reviewed:** 2026-11-13 (example-specific documentation). **Not runtime-tested here:** this illustrative workflow was not installed or triggered in a practice GitHub repository.
- Do not interpret this example as a recommended replacement for Awesome Tech Atlas's existing validation workflow. It does not change the catalog's earlier official-page inspection date.

## Where to go next

- Read the [upstream documentation](https://docs.github.com/en/actions) for setup, compatible versions, and API details.
- **Alternative:** [Git reference](git.md). Git is the underlying history and review mechanism; CI is an additional quality gate.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
