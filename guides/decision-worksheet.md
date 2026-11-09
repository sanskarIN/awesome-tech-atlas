# Technology decision worksheet

A comparison should answer **"for this requirement, which option is appropriate?"**, not **"which tool is best?"** Start with requirements and evidence. Use the [comparison index](../comparisons/README.md) and upstream references; avoid scoreboards detached from a real scenario.

## 1. Describe the job before naming tools

Write down:

- **Problem and audience:** what must happen, and who will use or maintain it?
- **Environment:** runtime, operating systems, offline/online needs, and available infrastructure.
- **Hard constraints:** compatibility, access-control needs, budget, deployment restrictions, or language requirements.
- **Success criteria:** observable outcomes such as "a test user can recover data after restart" or "a new contributor can run the example".
- **Scale assumptions:** input sizes, expected concurrency, and current uncertainties. Label every estimate as an estimate.

Do not transform an unknown into a fact merely to make one candidate look stronger.

## 2. Build a small evidence table

| Question | Candidate A | Candidate B | Evidence / uncertainty |
| --- | --- | --- | --- |
| Can it satisfy the non-negotiable requirements? | Yes / no / unknown | Yes / no / unknown | Official references or a reproducible test |
| How will it be deployed and maintained? | Specific tasks | Specific tasks | Setup/runbook evidence |
| What is the biggest failure mode? | Concrete risk | Concrete risk | Test plan and mitigations |
| Which skills or tools are missing? | Concrete gaps | Concrete gaps | Team inventory, not assumptions |
| What would change the decision? | Trigger | Trigger | Measurable threshold or new requirement |

A **no** on a genuine hard requirement is usually more informative than a weighted total. If both candidates remain viable, run the smallest experiment that distinguishes them.

## 3. Prototype the risky requirement

Use a tiny test dataset with the same important properties as the real workload, or a synthetic substitute where privacy matters.

1. Define the procedure *before* running it. Use the same input and acceptance criteria for each candidate.
2. Write down the exact versions and environment. Avoid comparing a tuned setup with an unconfigured one.
3. Verify correctness and safe failure behavior first; only then consider speed or resource usage if those metrics actually matter.
4. Repeat results and explain variability when performance is relevant.
5. Write down unknowns. A prototype result cannot establish security assurance, service availability, license compatibility, or production suitability by itself.

For one practical experiment, see the [Python versus Rust project options](project-based-tracks.md#track-1-python-command-line-data-summary) and the [Rust log inspector](project-based-tracks.md#track-4-rust-local-log-inspector).

## 4. Example: choosing embedded or server-side SQL

Suppose a small personal desktop program stores non-sensitive local notes. Two plausible options are [SQLite](../resources/sqlite.md) and [PostgreSQL](../resources/postgresql.md).

| Requirement | SQLite option | PostgreSQL option |
| --- | --- | --- |
| No separately managed database service | Fits the embedded approach | Normally needs server administration |
| Several independent clients across machines | Requires careful application architecture | Designed around client/server access |
| Operational owner for backup and recovery | Application team owns local-file strategy | Team owns server backup, permissions, upgrades |
| Unknown future hosting needs | Record as an uncertainty | Record as an uncertainty |

For the *stated local-only* program, SQLite is a reasonable **initial hypothesis** because fewer separate services are required. If independent networked clients or central administration become hard requirements, revisit the comparison. Neither conclusion is a performance benchmark or blanket endorsement.

**Upstream evidence to consult:** [SQLite documentation](https://www.sqlite.org/docs.html) and [PostgreSQL documentation](https://www.postgresql.org/docs/current/). Record the pages and dates you actually inspected before finalizing a real architecture decision.

## 5. Decision record template

Copy and complete this short structure:

> **Decision:** [specific choice for specific scenario]  
> **Date and owner:** [date / maintainer or team]  
> **Requirements:** [hard constraints and success metrics]  
> **Candidates:** [options considered]  
> **Evidence:** [official docs, runnable checks, version numbers, observations]  
> **Trade-offs:** [what we gain / what we knowingly accept]  
> **Unknowns:** [anything not yet verified]  
> **Revisit when:** [concrete change in requirement or observed outcome]

Use "not checked" where appropriate. Do not manufacture results, timings, popularity rankings, or security claims to complete the form.

## 6. Useful starting comparisons

- [Python versus Rust](../comparisons/README.md#python-vs-rust)
- [SQLite versus PostgreSQL](../comparisons/README.md#sqlite-vs-postgresql)
- [scikit-learn versus PyTorch versus JAX](../comparisons/README.md#scikit-learn-vs-pytorch-vs-jax)
- [NumPy versus SciPy versus scikit-learn](../comparisons/README.md#numpy-vs-scipy-vs-scikit-learn)
- [React versus browser APIs](../comparisons/README.md#react-vs-browser-apis)
- [Docker versus Kubernetes](../comparisons/README.md#docker-vs-kubernetes)

**Editorial note:** this is a lightweight design aid, not a legal, security, procurement, or licensing approval process. Follow [source-evidence rules](../docs/EDITORIAL_POLICY.md) when publishing choices.
