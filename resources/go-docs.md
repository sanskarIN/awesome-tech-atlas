# Go documentation

**Official source:** https://go.dev/doc/  
**Type:** official docs  
**Category:** [Programming languages](../categories/programming-languages.md) · Go language and tooling  
**Last official-page inspection:** 2026-11-24

## Why it matters

Go provides a compiled language and an integrated toolchain that make it practical to move from small programs to independently deployed command-line tools and services.

## Good fit

Developers learning service programming or command-line development who want modules, a built-in testing workflow and concurrency primitives.

## Strength and trade-off

- **Strength:** Tutorials lead from a first program to module creation and testing, with references available for more precise language and tooling questions.
- **Limitation:** Garbage collection and concurrent scheduling are not a substitute for measuring resource consumption; concurrency requires explicit reasoning about cancellation, shared state and error handling.

These are contextual selection notes, not independent benchmarks or platform compatibility guarantees.

## Try it

Follow the create-a-module tutorial and define a function that counts words in a slice of strings. Return a map and add a table-driven test covering repeated words and empty input. Run go test from the module directory, then try go test with an intentionally wrong expectation.

## Where to go next

- Read the [upstream material](https://go.dev/doc/) for prerequisites and current documentation.
- **Alternative:** [The Rust Programming Language](rust.md). Choose Rust when predictable resource ownership or avoiding a garbage-collected runtime is a key requirement.

**Verification scope:** The official documentation index, including module, testing and language reference links, was inspected; no Go installation or test execution was performed. Inspection date: 2026-11-24.
