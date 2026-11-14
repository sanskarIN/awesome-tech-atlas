# Crafting Interpreters

**Original author-published source:** https://craftinginterpreters.com/  
**Type:** learning guide (independent book; not a programming-language specification)  
**Category:** [Compiler development](../categories/compiler-development.md) · Language implementation  
**Last official-page inspection:** 2026-11-14

## Why it matters

Robert Nystrom's book teaches language implementation by constructing two interpreters for a small teaching language, Lox. It connects scanning, parsing, evaluation, scope, closures and classes to working implementations, then introduces bytecode and virtual-machine concerns. This is an author-maintained educational source rather than official documentation for an existing production language.

## Good fit

- Programmers who want to understand what an interpreter does between source text and program behavior.
- Learners comparing a tree-walk evaluator with a bytecode virtual machine.
- Language designers looking for a concrete sequence of implementation milestones.

## Strength and trade-off

- **Strength:** The same teaching language is implemented using two distinct execution strategies, making trade-offs tangible.
- **Limitation:** The examples are an educational language implementation, not a full treatment of industrial compilers, static type systems, security hardening, or production runtimes. The book's Java and C examples also require corresponding language knowledge.

These are selection notes, not independently measured performance or security claims.

## Try it

Start with the [table of contents](https://craftinginterpreters.com/contents.html), read the language overview, then follow the scanner chapter before attempting to build a full parser. For the illustrative source `var answer = 2 + 3;`, write down the expected categories of tokens (keyword, identifier, assignment, number, operator, terminator). Compare your list with the book's treatment of scanning. This is a reading and reasoning exercise; no interpreter was executed during this review.

## Where to go next

- Follow [Scanning](https://craftinginterpreters.com/scanning.html) and [Parsing Expressions](https://craftinginterpreters.com/parsing-expressions.html) in order; later chapters depend on earlier concepts.
- **Alternative:** [LLVM documentation](llvm.md) focuses on compiler intermediate representation and backend infrastructure rather than the teaching interpreter pipeline.

**Verification scope:** The author-published book page, introduction and chapter index were reviewed on 2026-11-14. Examples and runtime behavior were not independently executed; the original book and code remain under their upstream terms. The CC0 dedication of this atlas covers only this original summary.
