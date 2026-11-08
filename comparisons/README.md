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
