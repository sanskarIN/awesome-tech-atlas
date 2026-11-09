# The Rust Programming Language

**Official source:** https://doc.rust-lang.org/book/  
**Type:** official guide  
**Category:** [Programming languages](../categories/programming-languages.md) · Rust language  
**Last official-page inspection:** 2026-11-08

## Why it matters

The official Rust book explains ownership, borrowing, types, error handling, and application development.

## Good fit

Learning memory-safe native programming and Rust project structure.

## Strength and trade-off

- **Strength:** Connects language concepts to Cargo-based programs and runnable examples.
- **Limitation:** Ownership and lifetime rules can take additional practice; native library interoperability has its own constraints.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Install Rust using the official setup instructions, then try `cargo new hello_atlas` followed by `cargo run` inside the project.


## Worked example: count warning lines in a local log

### Prerequisites

- A Rust toolchain with Cargo, installed using the [official instructions](https://www.rust-lang.org/tools/install).
- A plain-text editor and a local folder you can write to. No external crates or internet services are used by the program.

### Steps

1. Create a Cargo binary with \`cargo new atlas-log-count\` and open its directory.
2. Replace \`src/main.rs\` with this original program:

~~~rust
use std::{env, error::Error, fs};

fn main() -> Result<(), Box<dyn Error>> {
    let Some(path) = env::args().nth(1) else {
        eprintln!("Usage: cargo run -- sample.log");
        std::process::exit(2);
    };

    let contents = fs::read_to_string(path)?;
    let total = contents.lines().count();
    let warnings = contents
        .lines()
        .filter(|line| line.starts_with("WARN:"))
        .count();

    println!("lines: {total}\nwarnings: {warnings}");
    Ok(())
}
~~~

3. Create \`sample.log\` next to \`Cargo.toml\` containing exactly:

~~~text
INFO: ready
WARN: slow query
WARN: retry
~~~

4. From that directory run \`cargo run -- sample.log\`.

### Expected result

~~~text
lines: 3
warnings: 2
~~~

### Troubleshooting

- If Cargo cannot find \`sample.log\`, check that the working directory is the project root.
- If a file-reading error is shown, verify its path, encoding (UTF-8), and file permissions.
- This is a case-sensitive line-prefix match, not a general log parser. It assumes trusted, local UTF-8 test data.

### Evidence and execution status

- **Primary references:** [Rust book: reading a file](https://doc.rust-lang.org/book/ch12-02-reading-a-file.html) and [improving error handling](https://doc.rust-lang.org/book/ch12-03-improving-error-handling-and-modularity.html).
- **Reviewed:** 2026-11-09 (example-specific documentation). **Not runtime-tested here:** a Rust toolchain was not available in the execution environment. Output above is the expected result for the supplied file.
- No performance, cross-platform compilation, or production reliability claims are made. The catalog's earlier official-source inspection date remains unchanged.

## Where to go next

- Read the [upstream documentation](https://doc.rust-lang.org/book/) for setup, compatible versions, and API details.
- **Alternative:** [Python documentation](python.md). Python often makes an easier first tool for small scripts and interactive data exploration.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
