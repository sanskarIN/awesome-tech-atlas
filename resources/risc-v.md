# RISC-V unprivileged ISA specification

**Official source:** https://docs.riscv.org/reference/isa/v20260120/unpriv/unpriv-index.html  
**Type:** specification  
**Category:** [Computer architecture](../categories/computer-architecture.md) · Instruction-set architecture  
**Last official-page inspection:** 2026-11-08

## Why it matters

Official unprivileged RISC-V instruction-set manual for architectural behavior and extensions.

## Good fit

Studying how machine instructions and registers are specified independent of a particular CPU.

## Strength and trade-off

- **Strength:** Normative ISA material establishes a clear reference for architecture discussion.
- **Limitation:** An ISA specification is not a CPU design guide or a guarantee that every implementation supports every extension.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Read the specification's preamble and distinguish base integer instructions from optional extensions.

## Where to go next

- Read the [upstream documentation](https://docs.riscv.org/reference/isa/v20260120/unpriv/unpriv-index.html) for setup, compatible versions, and API details.
- **Alternative:** [LLVM documentation](llvm.md). LLVM documentation covers code generation to target architectures from compiler IR.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
