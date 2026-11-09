# Comparison guides

**These are scenario-based editorial choices, not benchmarks or universal rankings.** Features, licenses, prices, and performance may change. Read each resource's official documentation before committing to an architecture.

## Python vs Rust

| Need | Usually start with | Why / what to watch |
| --- | --- | --- |
| Short scripts, interactive notebooks, data analysis | [Python](../resources/python.md) | Broad scientific ecosystem; runtime and packaging needs can matter |
| Native binaries, memory-safety-sensitive systems code | [Rust](../resources/rust.md) | Ownership rules add a learning curve; FFI/ecosystem availability should be checked |
| Python orchestration with native hot paths | Both | Profile before rewriting; a boundary between languages adds integration work |

## SQLite vs PostgreSQL

| Need | Usually start with | Why / what to watch |
| --- | --- | --- |
| Local, embedded, single-file relational storage | [SQLite](../resources/sqlite.md) | No separate server; concurrency and deployment patterns differ from client/server DBs |
| A service handling many concurrent clients and centralized DB access | [PostgreSQL](../resources/postgresql.md) | Rich server capabilities; adds operations and access control |
| Prototyping that will later be hosted | Depends | Make migrations and concurrency requirements explicit before deciding |

## scikit-learn vs PyTorch vs JAX

- [scikit-learn](../resources/scikit-learn.md): first stop for established conventional ML estimators and evaluation tooling.
- [PyTorch](../resources/pytorch.md): tensor-first deep-learning workflows and model training.
- [JAX](../resources/jax.md): array computing with program transformations such as gradients and JIT compilation.

They are **not interchangeable** replacements: the learning and deployment costs depend on the task. Compare measured outcomes on your own workload rather than repeating online speed claims.

## Docker vs Kubernetes

[Docker](../resources/docker.md) introduces image/container packaging; [Kubernetes](../resources/kubernetes.md) is an orchestration platform that coordinates containerized workloads across infrastructure. A small service does not inherently need Kubernetes.

## NumPy vs SciPy vs scikit-learn

These tools often complement each other rather than compete:

| Primary task | Start by studying | Boundary to understand |
| --- | --- | --- |
| N-dimensional arrays and array operations | [NumPy](../resources/numpy.md) | Arrays alone do not provide a complete model-evaluation workflow |
| Numerical algorithms such as optimization and scientific routines | [SciPy](../resources/scipy.md) | Understand input arrays and numerical assumptions before interpreting output |
| Standard estimators, preprocessing, and model selection | [scikit-learn](../resources/scikit-learn.md) | Leakage controls, splits, and metrics matter more than the choice of package name |

**Official references:** [NumPy manual](https://numpy.org/doc/stable/), [SciPy documentation](https://docs.scipy.org/doc/scipy/), and [scikit-learn documentation](https://scikit-learn.org/stable/). Read the relevant API pages for your installed versions, rather than assuming "latest" matches a frozen environment.

## React vs browser APIs

| Project need | Consider | Check before choosing |
| --- | --- | --- |
| Small page with a few event handlers | [MDN web platform guides](../resources/mdn-learn.md) | Component abstractions may not be necessary; still test state and accessibility |
| UI made of reusable stateful components | [React Learn](../resources/react.md) | Setup, data flow, deployment, and state ownership add decisions |
| Existing established team codebase | Its current framework or browser APIs | Migration cost and maintainers' familiarity matter; avoid rewriting without a demonstrated need |

**Official references:** [React's component and state guide](https://react.dev/learn) and [MDN's web curriculum](https://developer.mozilla.org/en-US/docs/Learn_web_development). A shared sample task and keyboard test are more informative than an unsubstantiated "faster" claim.

## From a comparison to an actual decision

Use the [technology decision worksheet](../guides/decision-worksheet.md) to record hard constraints, source evidence, one differentiating prototype, and a reason to revisit the choice. For guided practice, choose a [project-based track](../guides/project-based-tracks.md). These choices are context-dependent and may change with requirements.
