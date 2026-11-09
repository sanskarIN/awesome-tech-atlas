# Learning paths

A learning path is an **editable sequence**, not a universal curriculum. Pick one according to your goals; treat linked resources as references rather than homework to complete in full. When ready to build, follow the [project-based tracks](project-based-tracks.md) and record what you actually tested.

## Path A: New to software development

1. Learn core language fundamentals from [Python](../resources/python.md) or [JavaScript (MDN)](../resources/javascript-mdn.md). Practice variables, functions, loops, and reading errors.
2. Learn the shell, editor, and debugging basics in [The Missing Semester](../resources/missing-semester.md).
3. Learn commits, branches, and collaboration in [Git](../resources/git.md).
4. Build one small project and document how to run it. Explore [VS Code](../resources/vscode.md) if you need an editor.

**Outcome:** write, run, explain, and version-control a small program.

## Path B: Data and machine learning

1. Work with Python values, functions, files, and virtual environments.
2. Use [NumPy](../resources/numpy.md) to understand arrays and shapes.
3. Use [scikit-learn](../resources/scikit-learn.md) for a small regression/classification experiment with a train/test split.
4. Learn tensors and autodifferentiation using [PyTorch](../resources/pytorch.md); explore [JAX](../resources/jax.md) for functional array transformations.
5. Explain data quality, leakage, evaluation, and limitations in your report.

**Outcome:** reproduce a small experiment with explicit inputs, metrics, and caveats.

## Path C: Systems and infrastructure

1. Learn [Rust](../resources/rust.md) or a systems language and understand pointers, memory layout, error handling, and I/O.
2. Consult [Linux Kernel documentation](../resources/linux-kernel-docs.md) to understand processes and kernel interfaces.
3. Learn the compiler pipeline through [LLVM](../resources/llvm.md).
4. Containerize a toy service with [Docker](../resources/docker.md), then learn why [Kubernetes](../resources/kubernetes.md) exists for orchestration.

**Outcome:** explain how a program is compiled, runs on an OS, and is deployed.

## Path D: Web development and interface accessibility

1. Learn HTML semantics, CSS layout, JavaScript, and keyboard interaction in [MDN Learn](../resources/mdn-learn.md).
2. Make a simple interactive page with browser APIs and write down the state and event-handling decisions.
3. Learn [React](../resources/react.md) components, props, lists, and state; rebuild only the relevant behavior in a configured React environment.
4. Test keyboard use, visible focus, labels, updates, and empty states. Avoid claiming complete accessibility from a single test.
5. Keep a short README with browser versions, test results, and what happens on refresh.

**Outcome:** explain the trade-offs between a browser-native implementation and a component library, with a documented interaction test.

## Path E: Open-source maintenance

1. Learn branch-based collaboration with [Git](../resources/git.md) and the practical guidance in [Open Source Guides](../resources/open-source-guides.md).
2. Read a project's contribution policy and inspect an existing issue or documentation gap before proposing a change.
3. Review the [GitHub Actions](../resources/github-actions.md) workflow used to validate proposed changes.
4. Contribute one original, evidence-backed improvement via a PR without copying upstream material or exposing sensitive data.
5. Capture the tests, source references, and limitations in your PR description.

**Outcome:** submit a reviewable, reproducible documentation or tooling improvement.

See also the [decision worksheet](decision-worksheet.md) for evaluating tools for a specific use case, and the [five project tracks](project-based-tracks.md) for concrete milestones.

Avoid starting with everything at once. Verify new tools against the upstream documentation for your environment.
