# Applied engineering labs: validate, debug, review, and scan

These four short labs bridge curated documentation and **evidence you can reproduce**. They are optional companions to the [project-based tracks](project-based-tracks.md), not a universal learning sequence. Work with original, synthetic inputs in disposable directories, and record what you actually ran. The commands are **suggested exercises**, not claims that the Atlas authors executed them on your platform.

| Lab | What you build | Starting references | Evidence to keep |
| --- | --- | --- | --- |
| 1. TypeScript input boundary | A typed parser for an untrusted value | [TypeScript](../resources/typescript.md) | Accepted/rejected sample matrix |
| 2. C and GDB failure trace | A native program with one intentional logic bug | [CMake Tutorial](../resources/cmake-tutorial.md), [GNU GDB](../resources/gdb.md) | Before/after output and debugger observations |
| 3. Form accessibility review | A local labeled form with feedback | [W3C WAI tutorials](../resources/wai-tutorials.md), [MDN Learn](../resources/mdn-learn.md) | Keyboard and label inspection notes |
| 4. Tiny tokenizer | A scanner for a small original toy language | [Crafting Interpreters](../resources/crafting-interpreters.md) | Token stream, malformed-input tests, limitations |

All four labs separate **expected results** from **observed results**. Verify tool versions, platform behavior, and accessibility with your own environment before documenting an observed success.

## Lab 1: Validate untrusted records with TypeScript

### Goal and prerequisites

Accept only records with a nonempty string title and a positive, safe-integer page count. Learn why a TypeScript type is not a runtime validator. You need Node.js and an installed TypeScript compiler. Refer to the [TypeScript compiler and narrowing documentation](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) and the existing [TypeScript profile example](../resources/typescript.md#worked-example-narrow-unknown-input-before-using-it). The example uses no external runtime packages.

### Steps

1. Create an empty local directory and save the following original example as **records.ts**.
2. Compile it using the command below. The shell must be able to find the TypeScript compiler.
3. Run the generated JavaScript with Node.js.
4. Add a fifth case where the page count is zero; write down why it should be rejected before rerunning.

~~~sh
tsc --strict --target ES2022 --module commonjs records.ts
node records.js
~~~

~~~typescript
type BookRecord = { title: string; pages: number };

function parseRecord(value: unknown): BookRecord | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }

  const candidate = value as Record<string, unknown>;
  if (typeof candidate.title !== "string" || candidate.title.trim() === "") {
    return null;
  }
  if (
    typeof candidate.pages !== "number" ||
    !Number.isSafeInteger(candidate.pages) ||
    candidate.pages < 1
  ) {
    return null;
  }

  return { title: candidate.title.trim(), pages: candidate.pages };
}

const inputs: unknown[] = [
  { title: "Field notes", pages: 3 },
  { title: "Unvalidated", pages: "3" },
  null,
  { title: "", pages: 1 },
];

console.log(JSON.stringify(inputs.map(parseRecord)));
~~~

### Expected result and diagnostic cases

~~~text
[{"title":"Field notes","pages":3},null,null,null]
~~~

| Input | Expected | Why |
| --- | --- | --- |
| A nonempty title and numeric page count of 3 | Accepted | Both runtime checks pass |
| A title with a string page count of "3" | Rejected | A string is not accepted as a number |
| A null value | Rejected | It is not a record to inspect |
| A blank title | Rejected | Trimming leaves no characters |
| A page count of 0 | Rejected | This lab requires a positive count |

The type assertion only permits checking candidate properties; it does **not** make the unknown value safe. The runtime checks establish the local toy contract. Add edge cases for arrays, fractional numbers, and values beyond the safe-integer range.

### Evidence and limitations

Keep the actual compiler/runtime versions, command used, output and any differences. This example does not enforce a complete schema, persist data, or protect a real network endpoint. A broader application needs validation at each relevant trust boundary. **Execution status:** this example is provided for learner reproduction; the Atlas has not recorded an independent execution result for this lab.

## Lab 2: Trace a C logic defect with CMake and GDB

### Goal and prerequisites

Find an off-by-one bug by **observing the loop**, not guessing. Use a disposable local directory with a compatible C compiler, CMake and GNU GDB already available. The [CMake tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/) explains configure/build separation; the [GDB manual](https://sourceware.org/gdb/current/onlinedocs/gdb/) covers breakpoints, stepping and inspecting state.

### Steps

1. Save these two original files in the same empty directory.
2. Configure a debug build and build the target. CMake is not a C compiler; you must supply a suitable toolchain.
3. Run the program. Its initial failure is deliberate, so record its output and nonzero exit status.
4. Start GDB on the actual executable path. The location differs by generator and platform.
5. Set a breakpoint, advance through iterations, and inspect the loop variable and accumulated sum **after each update**.
6. Correct the condition, rebuild, rerun, and compare the evidence.

**CMakeLists.txt**

~~~cmake
cmake_minimum_required(VERSION 3.16)
project(AtlasTrace LANGUAGES C)
add_executable(atlas_trace main.c)
~~~

**main.c**

~~~c
#include <stdio.h>

static int sum_through(int last) {
    int total = 0;
    for (int value = 1; value < last; ++value) {
        total += value;
    }
    return total;
}

int main(void) {
    int observed = sum_through(5);
    printf("observed=%d expected=15\n", observed);
    return observed == 15 ? 0 : 1;
}
~~~

For a single-configuration generator that honors the build type, the commands are:

~~~sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
./build/atlas_trace
gdb ./build/atlas_trace
~~~

For a multi-configuration generator, use **cmake --build build --config Debug** and locate the generated executable, often under a Debug subdirectory. On Windows, executable suffixes and available debuggers vary; substitute the matching platform commands rather than assuming this Unix-style path works everywhere.

Once GDB has opened the executable, an illustrative command sequence is:

~~~text
break sum_through
run
next
next
print last
print total
continue
quit
~~~

Breakpoints and the exact number of **next** commands depend on your toolchain and source line positions. Set a breakpoint on the accumulation statement or step repeatedly to observe **value** and **total** at the correct point in the loop. Do not expect local variable values to be meaningful before initialization.

### Expected result and diagnostic cases

Initially the loop adds 1, 2, 3, and 4, producing:

~~~text
observed=10 expected=15
~~~

The executable should return an error status because 10 differs from 15. After changing **value < last** to **value <= last**, the expected line becomes:

~~~text
observed=15 expected=15
~~~

The corrected executable should then return zero. Try additional cases for **last = 0**, **last = 1**, and **last = 2**, and write down what result your function is intended to return for each before adding automated assertions.

### Evidence and limitations

Record the compiler name/version, CMake version, generator, debugger version, before/after output and at least two observed loop states. Optimizations can move or hide variables even when debugging is enabled; platform and debugger support differ. This lab demonstrates a **logic error**, not memory safety, performance profiling, or production debugging coverage. **Execution status:** no platform-specific build or GDB session is claimed to have been executed by the Atlas for this lab.

## Lab 3: Review a local form for accessible interaction

### Goal and prerequisites

Create a small form, then investigate whether visible labels, instructions, focus, required fields and feedback work for a keyboard user. Use a local file in a modern browser. Read the [WAI forms tutorial](https://www.w3.org/WAI/tutorials/forms/) and the [WAI labeling guidance](https://www.w3.org/WAI/tutorials/forms/labels/) first; consult [MDN Learn](../resources/mdn-learn.md) for broader HTML and event handling.

### Steps

1. Save the following original page as **form.html**. The input is a harmless invented topic name, not personal or sensitive information.
2. Open it locally; no backend or network request is needed.
3. Use Tab and Shift+Tab to move focus; check whether the input and button can be reached in a sensible order.
4. Submit with the field empty, with spaces only, and with a normal topic name. Note the browser's built-in required-field feedback and the page's custom status message separately.
5. Inspect whether the visible label is programmatically associated with the input. Then perform at least one assistive-technology check if you have access to the relevant setup.

~~~html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Local topic form</title>
<h1>Choose a practice topic</h1>
<form id="topic-form">
  <label for="topic">Practice topic</label>
  <p id="topic-help">Enter a short invented topic name.</p>
  <input id="topic" name="topic" required maxlength="60"
         aria-describedby="topic-help">
  <button type="submit">Check entry</button>
</form>
<p id="result" role="status" aria-live="polite"></p>
<script>
const form = document.getElementById("topic-form");
const topic = document.getElementById("topic");
const result = document.getElementById("result");

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const cleaned = topic.value.trim();
  result.textContent = cleaned
    ? "Local entry accepted: " + cleaned
    : "Enter a nonblank practice topic.";
});
</script>
</html>
~~~

### Expected result and diagnostic cases

| Action | Expected observation | What to verify manually |
| --- | --- | --- |
| Tab through the page | Input and button receive focus | Focus visibility and sensible order |
| Submit an empty required field | Browser prevents normal submission | Understand the browser's native validation message |
| Submit spaces only | Page reports a nonblank requirement | Message is visible and conveyed by your tested assistive technology |
| Submit a topic such as "Arrays" | Page shows the accepted text | No network call; only local text is changed |
| Refresh the page | In-memory status resets | No persistence is claimed |

The sample deliberately uses **textContent** rather than interpreting input as HTML. That is good for this particular output boundary, but does not constitute a complete security review.

### Evidence and limitations

Write down browser/OS versions, keyboard observations, any assistive-technology tool/version, and any issue you could reproduce. A **role=status** region does not guarantee identical announcements in all browser and screen-reader combinations. Native validation interfaces vary. The exercise is not a WCAG conformance audit, certification, or a replacement for testing with people who use assistive technology. **Execution status:** no real browser or screen-reader run is asserted for this lab.

## Lab 4: Scan a tiny language with Python

### Goal and prerequisites

Build a lexer for a deliberately tiny invented syntax before considering parsing or evaluation. The goal is to classify tokens, preserve their order, and report unexpected characters. Use **Python 3.10+** and the standard library; no code will be executed from untrusted input. For the conceptual distinction between scanning and parsing, consult the author-published [Crafting Interpreters scanning chapter](https://craftinginterpreters.com/scanning.html) and [compiler infrastructure documentation](../resources/llvm.md). The following implementation is **original educational code**, not copied from an upstream book.

### Steps

1. Create **scan.py** using the complete example below.
2. Run it locally with Python. Compare the printed tokens to the expected sequence.
3. Modify the input to include an invalid character and confirm that the lexer produces an informative error instead of silently discarding it.
4. Add a test for a multi-digit number, an identifier containing an underscore, and a semicolon.
5. Document which syntax you intentionally do not support.

~~~python
import re

TOKEN = re.compile(
    r"(?P<SPACE>\s+)"
    r"|(?P<NUMBER>[0-9]+)"
    r"|(?P<NAME>[A-Za-z_][A-Za-z_0-9]*)"
    r"|(?P<EQUALS>=)"
    r"|(?P<PLUS>\+)"
    r"|(?P<SEMICOLON>;)"
    r"|(?P<BAD>.)"
)


def scan(source: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    for match in TOKEN.finditer(source):
        kind = match.lastgroup
        value = match.group()
        if kind == "SPACE":
            continue
        if kind == "BAD":
            raise ValueError(
                f"unexpected character {value!r} at offset {match.start()}"
            )
        if kind == "NAME" and value == "let":
            kind = "LET"
        assert kind is not None
        tokens.append((kind, value))
    return tokens


if __name__ == "__main__":
    text = "let total = 12 + 3;"
    print(scan(text))
    assert scan("let x_1 = 2;")[-1] == ("SEMICOLON", ";")
    try:
        scan("let x = @")
    except ValueError as error:
        print(error)
    else:
        raise AssertionError("invalid character was not rejected")
~~~

### Expected result and diagnostic cases

~~~text
[('LET', 'let'), ('NAME', 'total'), ('EQUALS', '='), ('NUMBER', '12'), ('PLUS', '+'), ('NUMBER', '3'), ('SEMICOLON', ';')]
unexpected character '@' at offset 8
~~~

| Input | Expected behavior |
| --- | --- |
| **let total = 12 + 3;** | Seven tokens in source order |
| **let x_1 = 2;** | Identifier with underscore, semicolon at the end |
| **let x = @** | Explicit exception with source offset |
| An empty string | An empty token sequence |
| A decimal such as **1.5** | Rejected at the decimal point; floats are not supported |

### Evidence and limitations

Retain the Python version, real output, input matrix, and explanation of the intentionally limited grammar. This lexer is **not a parser**, interpreter, compiler, sandbox, or production language toolchain. It does not process comments, strings, floating-point numbers, Unicode identifiers, or arbitrarily large source files with line/column diagnostics. Failure on these inputs is a defined learning boundary, not evidence of a defect in another language's compiler. **Execution status:** the code is statically checked for Python syntax by the Atlas test suite, but this guide does not claim that its runtime output has been independently reproduced.

---

## Keep a reproducibility record

For whichever lab you attempt, write an evidence card containing:

| Field | Record |
| --- | --- |
| Task and input | Lab name and specific synthetic input |
| Environment | OS, tool/runtime versions and relevant setup |
| Steps performed | Commands and manual checks actually used |
| Expected versus observed | Predicted result next to real output or interaction |
| Failure or surprise | A reproduced error and what changed to resolve it |
| Limits | Untested conditions and why the result may not generalize |
| Next experiment | One small, testable follow-up question |

A passing toy project is not a product security approval, a performance benchmark or proof of accessibility conformance. To choose tools for an actual application, return to the [technology decision worksheet](decision-worksheet.md). To find source explanations and alternatives, consult the [resource index](../resources/README.md).

**Source and authorship note:** the linked reference pages explain relevant technologies; this guide's exercises and code were written for the Atlas. The Atlas does not copy upstream examples into its CC0 work or change catalog inspection dates when adding a guide.