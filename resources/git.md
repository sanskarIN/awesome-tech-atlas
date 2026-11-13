# Git reference

**Official source:** https://git-scm.com/docs  
**Type:** official docs  
**Category:** [Software engineering](../categories/software-engineering.md) · Version control  
**Last official-page inspection:** 2026-11-08

## Why it matters

Upstream reference for Git commands, branching, merges, rebases, and repository history.

## Good fit

Tracking changes, reviewing patches, and collaborating on software.

## Strength and trade-off

- **Strength:** Detailed command reference clarifies how Git operations work.
- **Limitation:** It is a reference, not a substitute for a safe collaboration workflow or team conventions.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

In a practice repository, run `git status`, make a text change, and inspect it with `git diff`.

## Worked example: inspect a change before committing

### Prerequisites

- Git 2.28+ and a POSIX-style shell (Linux, macOS or Git Bash on Windows). This uses a disposable **new directory**, not an existing repository.
- An editor is optional; all sample file content is created by the commands. Git's `-b` initial-branch option is supported in the stated Git range.

### Steps

Run the following from a directory where the new `atlas-diff-demo` folder does not already exist:

~~~sh
git init --quiet -b main atlas-diff-demo
cd atlas-diff-demo
printf 'alpha\n' > notes.txt
git add notes.txt
git -c user.name='Atlas Example' -c user.email='atlas@example.invalid' \
  commit --quiet -m 'Initial notes'
printf 'beta\n' >> notes.txt
git diff --name-only
git diff --check
git status --short
~~~

The author identity is supplied **for this one practice commit only**; no global Git configuration is changed. `git diff` compares the uncommitted working-tree content with the index, while `git diff --check` looks for whitespace errors.

### Expected result

`git diff --name-only` prints `notes.txt`. With the exact sample content, `git diff --check` prints nothing and `git status --short` prints ` M notes.txt` (a modified, unstaged tracked file). The initial commit command is quiet.

### Troubleshooting

- If the directory already exists, choose a new practice folder instead of reusing or deleting an existing project.
- If `git init -b` is unsupported, update Git or initialize an empty repository and set the branch name separately.
- `git diff` without `--cached` does **not** show changes that have already been staged. Check `git diff --cached` when reviewing staged edits.
- These commands are intended for a practice folder. Always review the current path and working tree before applying Git operations to real work.

### Evidence and execution status

- **Primary references:** [Git diff manual](https://git-scm.com/docs/git-diff) and [Git init manual](https://git-scm.com/docs/git-init).
- **Reviewed:** 2026-11-13 (example-specific documentation). **Executed locally:** Git 2.47.3 in a disposable temporary directory; observed `notes.txt`, a clean whitespace check and ` M notes.txt`.
- This example demonstrates local diff inspection only, not multi-author collaboration or conflict resolution. The original catalog inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://git-scm.com/docs) for setup, compatible versions, and API details.
- **Alternative:** [GitHub Actions documentation](github-actions.md). GitHub Actions complements Git by testing changes; it is not a version-control replacement.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
