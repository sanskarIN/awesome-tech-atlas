# Microsoft C++ documentation

**Official source:** https://learn.microsoft.com/en-us/cpp/cpp/  
**Type:** official docs  
**Category:** [Programming languages](../categories/programming-languages.md) · C++ language and MSVC  
**Last official-page inspection:** 2026-11-24

## Why it matters

C++ supports abstraction while retaining control over object lifetime and native resource usage. This documentation helps readers connect language rules with compiler diagnostics and library interfaces.

## Good fit

Developers learning native applications with Visual Studio or maintaining C++ projects who want a practical entry into language and standard-library topics.

## Strength and trade-off

- **Strength:** Compiler, language and standard-library navigation are available together; readers can investigate an error without confusing the compiler with the language specification.
- **Limitation:** MSVC extensions and platform-specific examples are not guaranteed portable. Modern C++ feature availability depends on compiler version and selected language mode.

These are contextual selection notes, not independent benchmarks or platform compatibility guarantees.

## Try it

Use the console-project instructions, then write a small program using std::vector<int> and a range-based loop to compute a total. Compile with warnings enabled and compare empty and nonempty input. Next investigate how passing a const reference differs from copying the vector.

## Where to go next

- Read the [upstream material](https://learn.microsoft.com/en-us/cpp/cpp/) for prerequisites and current documentation.
- **Alternative:** [Microsoft C language documentation](c-msvc.md). Choose the C reference if the target codebase requires C compatibility and does not use C++ classes or library abstractions.

**Verification scope:** The vendor index for C++ language, standard library and compiler tools was inspected; code samples were not built or benchmarked. Inspection date: 2026-11-24.
