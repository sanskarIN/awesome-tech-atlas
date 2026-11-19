# Evidence-led specialization paths

These six paths extend the [general learning paths](learning-paths.md) with small, reviewable decisions in areas that a single-language tutorial may not cover. They use **existing curated Atlas profiles**, not an unverified list of new tools. Every exercise is a proposal for the reader to test, not a claim that this repository has run it.

Choose one path based on a real question. Use synthetic or explicitly authorized inputs, retain the evidence, and stop when you can explain a limitation. None of the paths requires a cloud account, a public deployment, or real user data.

## Path 1: Choose a mobile UI stack

**Question:** Is a platform-specific Android implementation or a multi-platform UI toolkit justified by the application you are actually building?

**References:** [Android Developers](../resources/android-dev.md) and [Flutter documentation](../resources/flutter.md). The two sources teach different development models; a UI toolkit does not eliminate platform-specific permissions, integration work, or maintenance.

1. Write down the target platforms, minimum accessibility needs, offline behavior, distribution constraints, and who will maintain the application.
2. Sketch one tiny app with a list, an empty state, a labeled input, a save action, and an error state. Keep all records synthetic and on-device for this exercise.
3. Follow the Android source's current getting-started guidance to estimate the project, toolchain, and emulator/device requirements. Do the same separately for Flutter. Record the documentation versions or pages consulted.
4. If both environments are available, implement the same interaction in each. Compare the behavior on back navigation, text scaling, keyboard or assistive interaction, app restart, and error recovery.
5. Record platform permissions and packaging requirements separately from the UI implementation. Do not interpret a passing emulator exercise as evidence of store approval, device compatibility, or accessibility conformance.

**Evidence to keep:** a requirements table, two small implementations or documented setup blockers, exact test platforms, and an explanation of which constraint decided the choice.

**Stop condition:** you can justify a stack for this app, while acknowledging why a different app could make a different choice. Do not select a toolkit solely from an unverified speed or popularity claim.

## Path 2: Compare deep-learning workflows without invented benchmarks

**Question:** Which model-building workflow matches a specified experiment and its constraints?

**References:** [TensorFlow Guide](../resources/tensorflow.md), [PyTorch documentation](../resources/pytorch.md), [JAX documentation](../resources/jax.md), and [scikit-learn](../resources/scikit-learn.md) for a conventional baseline.

1. Describe the task, shape and type of a tiny synthetic dataset, required device, model family, evaluation metric, and deployment environment before choosing software.
2. Read each project's current introductory and installation guidance. Record compatible language/runtime versions and any missing dependencies or hardware support.
3. Reproduce one modest tensor or differentiation operation **only in environments you can actually run**. Keep input values and expected mathematical results identical. Note API and debugging differences, without presenting them as performance rankings.
4. If the task is conventional tabular prediction, build a scikit-learn baseline with a split or cross-validation design that avoids fitting preprocessing on held-out examples. Do not assume deep learning must win.
5. If comparing implementations, control random seeds where possible, dataset splits, evaluation logic and device context. Say explicitly when an experiment was not run; never manufacture timing or accuracy numbers.

**Evidence to keep:** an environment matrix, a tested tiny example with actual output, train/evaluation boundary, decision criteria, and limitations.

**Stop condition:** distinguish documented features, personal development experience, and independently measured results. A toy experiment cannot establish broad production performance.

## Path 3: Reason about algorithms before optimizing

**Question:** Can you explain why a small algorithm is correct and where it fails?

**References:** [CP-Algorithms](../resources/cp-algorithms.md), [Python](../resources/python.md), and [The Missing Semester](../resources/missing-semester.md) for practical tests and debugging tools.

1. Choose a simple algorithmic problem such as reachability in an **unweighted** graph. State the accepted input shape and whether disconnected vertices are allowed.
2. Define three tiny graphs by hand: one connected, one with an isolated vertex, and one with a cycle. Write the expected reachable vertex sets before writing code.
3. Implement an uncomplicated traversal, keeping visited-state updates explicit. Test against the handwritten results, then test empty and malformed inputs according to your chosen contract.
4. Use the reference to learn the invariant and complexity of the method; explain why the conclusions change if the problem instead asks for shortest paths with arbitrary edge weights.
5. Capture a failing test before attempting an optimization, and compare correctness first. Make performance statements only if you design and run a reproducible measurement.

**Evidence to keep:** input contract, invariants, tests with observed output, complexity assumptions, and at least one known unsupported case.

**Stop condition:** another reader can reproduce the result and name the assumptions on which the algorithm depends.

## Path 4: Separate ISA, embedded software and operating systems

**Question:** Which layer is responsible for an instruction, a bare-metal program, and an operating-system service?

**References:** [RISC-V unprivileged ISA specification](../resources/risc-v.md), [The Embedded Rust Book](../resources/embedded-rust.md), [Linux kernel documentation](../resources/linux-kernel-docs.md), and [LLVM](../resources/llvm.md).

1. Draw a four-layer diagram: source code, compiler output/instruction semantics, machine or emulated execution environment, and operating-system services (if an OS exists).
2. Pick a small arithmetic or branch operation. Use the unprivileged ISA reference to explain instruction-level semantics, not device boot configuration or full system privileges.
3. Read the Embedded Rust material to see how a target, runtime startup, memory map, and device interfaces affect bare-metal development. Do not assume the book's sample target is RISC-V or that a host binary runs on a microcontroller.
4. Contrast the bare-metal path with a program using an OS service. Refer to the Linux kernel docs for kernel/user boundary concepts; avoid describing a particular kernel implementation as universal.
5. Label what remains outside scope: the privileged architecture, board-specific peripherals, linker scripts, interrupts, ABI details, and hardware validation. Use a simulator or paper exercise if the necessary hardware is unavailable.

**Evidence to keep:** a labeled layer diagram, one instruction walkthrough, a target-assumption list, and open questions for any unexamined layer.

**Stop condition:** you can explain why an instruction-set manual, an embedded programming guide and kernel documentation are **complementary rather than substitutes**.

## Path 5: Observe the behavior you own

**Question:** Do you need application-level telemetry, packet inspection, or both for a specific failure?

**References:** [OpenTelemetry documentation](../resources/opentelemetry.md) and [Wireshark documentation](../resources/wireshark.md).

1. Define an error in a tiny local application you control, such as an intentionally slow request with a synthetic identifier. State which question you want evidence to answer.
2. Draw a path from request to response and annotate where application events, spans and metrics could be collected. Explain which of those facts a network capture cannot reveal by itself.
3. Separately sketch the network-level facts a packet capture might show. A trace is not a packet capture, and encrypted traffic is not made readable by merely opening a packet analyzer.
4. If running an exercise, use only your own loopback or expressly authorized test traffic. Disable collection of real credentials, private messages and personal information; minimize retention.
5. Compare the evidence against your original question, record collection gaps and instrumentation overhead, and avoid claiming a complete diagnosis from one signal.

**Evidence to keep:** the failure question, a minimal signal map, test-only observations actually collected, privacy controls, and unknowns.

**Stop condition:** you can select a measurement tool based on the layer of the problem without assuming either tool is comprehensive.

## Path 6: Separate application security from repository practice

**Question:** Which security questions must be answered by application design, and which by open-source project governance?

**References:** [OWASP Cheat Sheet Series](../resources/owasp-cheatsheets.md), [OpenSSF Scorecard](../resources/openssf-scorecard.md), and [GitHub Actions](../resources/github-actions.md).

1. Model a small, fictional web application with a form, two roles and a server-side action. List expected trust boundaries and the consequences of invalid input or missing authorization.
2. Use the relevant OWASP guidance to draft defensive requirements for input handling, identity, authorization and secret management. Keep the exercise design-oriented: no live testing of third-party systems.
3. Independently review a sample repository's workflow and contribution controls. Use the Scorecard categories as prompts to collect visible evidence, not as a guarantee that the software is secure.
4. Write two separate checklists: **application behavior** and **repository/automation practice**. Describe who can verify each item and what remains unknown.
5. Revisit the [technology decision worksheet](decision-worksheet.md), document the highest-risk missing evidence, and propose one proportionate next test or review.

**Evidence to keep:** a threat-boundary sketch, defensive requirements, repository evidence, explicit unknowns, and a prioritized follow-up action.

**Stop condition:** you can explain why passing an automated repository check does not prove an application's behavior is safe.

---

## Evidence record for any specialization

Keep one short record per exercise. This makes a result reviewable without claiming that every tool or environment was tested.

| Field | Record |
| --- | --- |
| Question | The decision or failure you are investigating |
| Source boundary | Links to the official source pages you actually read, with inspection date |
| Environment | Versions, operating system, device or emulator where relevant |
| Input | Synthetic or expressly authorized test data and expected behavior |
| Observations | Exact outputs, screenshots or test logs you actually obtained |
| Limitations | Missing tests, unsupported platforms, incomplete threat model or unknowns |
| Decision | Current choice, rationale, and the condition that would make you reconsider |

For a smaller first task, use the [applied engineering labs](applied-engineering-labs.md). For a complete project with a definition of done, see the [project-based tracks](project-based-tracks.md). These paths are not certifications, product endorsements, or deployment instructions.
