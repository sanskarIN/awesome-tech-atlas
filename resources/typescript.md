# TypeScript documentation

**Official source:** https://www.typescriptlang.org/docs/  
**Type:** official docs  
**Category:** [Programming languages](../categories/programming-languages.md) · Typed JavaScript  
**Last official-page inspection:** 2026-11-08

## Why it matters

Official TypeScript handbook and references for a JavaScript type-checking language and toolchain.

## Good fit

Adding static analysis to JavaScript projects and maintaining larger codebases.

## Strength and trade-off

- **Strength:** The handbook covers everyday types, narrowing, generics, and compiler concepts.
- **Limitation:** Type annotations do not automatically validate untrusted runtime data; configuration matters.

These are contextual selection notes, **not** independent speed, reliability, or security benchmarks.

## Try it

Follow the Handbook's first steps, create a tiny `.ts` file, and run the type checker for your configured project.

## Worked example: narrow unknown input before using it

### Prerequisites

- TypeScript compiler (`tsc`) and Node.js installed following the [TypeScript setup guide](https://www.typescriptlang.org/docs/handbook/2/basic-types.html). The example was checked with TypeScript 5.8.3 and Node.js 22.16.0.
- A new empty directory; save this original example as `count.ts`. No libraries or network calls are used by the code.

### Steps

From that directory, compile with `tsc --strict --target ES2022 --module commonjs count.ts`, then run `node count.js`.

~~~typescript
function parseCount(value: unknown): number | null {
  if (typeof value !== "string") return null;
  const cleaned = value.trim();
  if (!/^\d+$/.test(cleaned)) return null;
  const count = Number(cleaned);
  return Number.isSafeInteger(count) ? count : null;
}

const samples: unknown[] = ["12", "oops", 12, "9007199254740992"];
console.log(JSON.stringify(samples.map(parseCount)));
~~~

`unknown` forces a runtime check before calling string methods. The regular expression allows only decimal digits, and `Number.isSafeInteger` rejects values outside JavaScript's safe-integer range.

### Expected result

~~~text
[12,null,null,null]
~~~

Try changing the second input to `"7"` and verify that only that result changes to `7`.

### Troubleshooting

- If `tsc` is not found, follow the compiler installation instructions and verify your shell can locate it.
- If compilation errors mention library targets, use the shown `--target ES2022` setting instead of an older project default.
- This is intentionally a narrow parser: it rejects negatives, decimals, localized digits and whitespace *inside* numbers. TypeScript annotations alone cannot validate network or user-supplied values.

### Evidence and execution status

- **Primary references:** [TypeScript handbook: narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) and [MDN: safe integers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isSafeInteger).
- **Reviewed:** 2026-11-13 (example-specific documentation). **Executed locally:** TypeScript 5.8.3 and Node.js 22.16.0; output matched the expected JSON.
- This smoke test does not establish compatibility with every TypeScript configuration or runtime. It does not change the catalog's earlier upstream inspection date.

## Where to go next

- Read the [upstream documentation](https://www.typescriptlang.org/docs/) for setup, compatible versions, and API details.
- **Alternative:** [MDN JavaScript](javascript-mdn.md). Learn JavaScript runtime behavior on MDN before assuming TypeScript types change execution.

**Verification scope:** The linked upstream documentation was inspected on 2026-11-08. Runtime behavior, licensing details for specific distributions, and installation on every platform were not independently tested. Check the project's official terms and release information before reuse or deployment.
