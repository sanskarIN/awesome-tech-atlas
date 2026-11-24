# Nand to Tetris

**Official source:** https://www.nand2tetris.org/  
**Type:** learning course  
**Category:** [Computer architecture](../categories/computer-architecture.md) · Computer construction from logic gates  
**Last official-page inspection:** 2026-11-24

## Why it matters

Building a simplified machine layer by layer reveals why Boolean logic, arithmetic, memory, instruction execution and software tools must agree on interfaces.

## Good fit

Students wanting a concrete bridge from digital logic to programming languages and operating-system abstractions; useful before exploring real instruction sets.

## Strength and trade-off

- **Strength:** The projects give each abstraction a concrete implementation target and make dependencies between hardware and software visible.
- **Limitation:** The educational machine deliberately simplifies modern hardware; its timing, memory hierarchy and instruction set should not be mistaken for those of a production CPU.

These are contextual selection notes, not independently measured performance or reliability claims.

## Try it

Open the project materials and begin with the first logic-gate exercise. Draw the truth table for a two-input NAND gate, then reason about constructing NOT using tied inputs. Use the course simulator to compare the predicted outputs with the exercise tests. Record mismatches before continuing.

## Where to go next

- Read the [upstream material](https://www.nand2tetris.org/) for prerequisites, current instructions and applicable terms.
- **Alternative:** [RISC-V unprivileged ISA specification](risc-v.md). Consult this specification when moving from the course's educational computer to a standardized real instruction-set architecture.

**Verification scope:** The official course landing page and links to project materials and tools were inspected; the simulator was not installed or run. Review upstream licensing conditions before redistributing any course materials. Inspection date: 2026-11-24.
