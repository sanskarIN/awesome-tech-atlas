# Operating Systems: Three Easy Pieces

**Original author-published source:** https://pages.cs.wisc.edu/~remzi/OSTEP/  
**Type:** learning guide  
**Category:** [Operating systems](../categories/operating-systems.md) · Operating-system concepts  
**Last official-page inspection:** 2026-11-24

## Why it matters

The book explains the abstractions between applications and physical hardware, making it easier to reason about processes, scheduling, shared state and persistent files.

## Good fit

Readers who can write small programs and want to understand operating systems before studying a production kernel. Basic C and command-line experience help with the exercises.

## Strength and trade-off

- **Strength:** Concepts are paired with exercises and projects so readers can reason about resource management and check their understanding.
- **Limitation:** The examples are educational abstractions; actual kernel behavior varies by implementation and platform, and completing the book does not make a kernel production-ready.

These are contextual selection notes, not independently measured performance or reliability claims.

## Try it

Start with the process abstraction and CPU scheduling chapters. On paper, trace two imaginary jobs of lengths 3 and 5 time units under first-come-first-served and compare their waiting times when the order is reversed. Then consult the relevant homework materials and document your assumptions.

## Where to go next

- Read the [upstream material](https://pages.cs.wisc.edu/~remzi/OSTEP/) for prerequisites, current instructions and applicable terms.
- **Alternative:** [Linux kernel documentation](linux-kernel-docs.md). Use kernel documentation after learning the abstractions, when you need implementation-specific interfaces and subsystem details.

**Verification scope:** The author-maintained landing page and its chapter and homework navigation were inspected; no course projects or kernel experiments were executed. Inspection date: 2026-11-24.
