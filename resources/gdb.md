# GNU GDB documentation

**Official source:** https://www.gnu.org/software/gdb/documentation/  
**Type:** official docs  
**Category:** [Developer tools](../categories/developer-tools.md) · Source-level debugging  
**Last official-page inspection:** 2026-11-14

## Why it matters

GNU GDB is a source-level debugger for examining program execution. Its documentation explains debugger commands, breakpoints, stepping, and inspection of program state, helping distinguish an observed failure from a guess about its cause.

## Good fit

- Debugging a locally built native program when appropriate debug information is available.
- Investigating a reproducible logic error one statement at a time.
- Learning how the compiler's debug information relates source lines to program state.

## Strength and trade-off

- **Strength:** The upstream manual covers an interactive, repeatable sequence of running, stopping and inspecting programs.
- **Limitation:** The quality of source-level inspection depends on available debug information and optimization settings. Supported targets and tool availability vary; GDB is not a substitute for testing or for debugging every language runtime.

These are contextual notes, not a claim that GDB supports every operating system, executable format or architecture.

## Try it

On a machine where a compatible C compiler and GDB are **already installed**, save a tiny program as `example.c`:

~~~c
int main(void) {
    int total = 2 + 3;
    return total == 5 ? 0 : 1;
}
~~~

Compile it with debug information using `cc -g -O0 example.c -o example`, then start `gdb ./example`. At the debugger prompt, try `break main`, `run`, `next`, `print total`, and `quit`. Depending on which statement is current, `total` may not yet have been initialized; step to its assignment before evaluating its value. This is a suggested local exercise, **not an executed test**; adjust the compiler or file name for your platform.

## Where to go next

- Consult the [official documentation page](https://www.gnu.org/software/gdb/documentation/) and the linked user manual for the debugger version installed on your system.
- **Alternative:** [Visual Studio Code documentation](vscode.md) describes editor debugging interfaces; the underlying debugger and installed extensions still determine the actual capabilities.

**Verification scope:** The GNU documentation listing and upstream GDB manual were reviewed through publicly available source listings on 2026-11-14. The local compile-and-debug exercise was not executed, and platform support, version-specific behavior, and package licenses must be checked upstream.
