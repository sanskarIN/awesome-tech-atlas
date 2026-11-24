# Kotlin basic syntax documentation

**Official source:** https://kotlinlang.org/docs/basic-syntax.html  
**Type:** official docs  
**Category:** [Programming languages](../categories/programming-languages.md) · Kotlin language  
**Last official-page inspection:** 2026-11-24

## Why it matters

Kotlin introduces concise typed expressions and explicit nullable types. The syntax overview gives readers a starting point for understanding how those ideas affect ordinary program structure.

## Good fit

Developers learning Kotlin before Android development or JVM application work, and Java programmers exploring a different language on a familiar platform.

## Strength and trade-off

- **Strength:** Small topic-focused examples link to more detailed language explanations, enabling incremental learning without first studying a large application framework.
- **Limitation:** The syntax overview is not a full build-tool or multiplatform deployment guide. A read-only variable does not imply that every object it refers to is immutable.

These are contextual selection notes, not independent benchmarks or platform compatibility guarantees.

## Try it

Write a function that converts an input string to a nullable integer using toIntOrNull, then returns either a doubled value or null. Test valid input, invalid text and an empty string; keep the return type explicit. Discuss how callers can handle the nullable result without a forced non-null assertion.

## Where to go next

- Read the [upstream material](https://kotlinlang.org/docs/basic-syntax.html) for prerequisites and current documentation.
- **Alternative:** [Dev.java learning tutorials](java-dev.md). Use Java tutorials when you need Java-specific JVM tools or want to compare equivalent application code across the two languages.

**Verification scope:** The upstream syntax page was read, including its sections about functions, variables, collections and null checks; suggested exercises were not executed. Inspection date: 2026-11-24.
