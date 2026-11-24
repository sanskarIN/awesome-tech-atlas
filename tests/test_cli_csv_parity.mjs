import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { resourcesToCsv, searchResources } from "../site/search.mjs";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const base = {
  category: "programming-languages",
  subcategory: "Reference materials",
  kind: "official-docs",
  url: "https://example.org/",
  verified_on: "2026-11-08",
};
const records = [
  { ...base, id: "alpha", name: "Alpha", summary: "A useful guide for learning" },
  {
    ...base, id: "beta", name: "Beta",
    subcategory: 'A "quoted", field',
    summary: "\t+SUM(1,2)", url: "https://example.org/beta",
  },
  {
    ...base, id: "gamma", name: "Gamma",
    summary: "A guide with Café and emoji 🚀", url: "https://example.org/gamma",
  },
];

function pythonCsv(filters, source = records) {
  const directory = mkdtempSync(join(tmpdir(), "atlas-csv-parity-"));
  try {
    const catalogPath = join(directory, "resources.json");
    writeFileSync(catalogPath, JSON.stringify(source), "utf8");
    const program = process.env.PYTHON || (process.platform === "win32" ? "py" : "python3");
    const prefix = !process.env.PYTHON && process.platform === "win32" ? ["-3"] : [];
    const args = [
      ...prefix, "scripts/atlas.py", "--catalog", catalogPath, "search", filters.query || "",
      ...(filters.category ? ["--category", filters.category] : []),
      ...(filters.kind ? ["--kind", filters.kind] : []),
      "--limit", String(Math.max(1, source.length)), "--csv",
    ];
    const result = spawnSync(program, args, { cwd: ROOT, encoding: "utf8" });
    assert.equal(result.error, undefined, String(result.error));
    assert.equal(result.status, 0, result.stderr);
    return result.stdout;
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
}

test("Python CLI and browser CSV are byte-for-byte aligned for full and filtered results", () => {
  for (const filters of [
    { query: "" },
    { query: "guide" },
    { query: "missing" },
    { query: "", category: "programming-languages" },
    { query: "", category: "web-development" },
  ]) {
    const browser = resourcesToCsv(searchResources(records, filters));
    assert.equal(pythonCsv(filters), browser, JSON.stringify(filters));
  }
});

test("CSV parity includes quotes, Unicode, and neutralized formula prefixes", () => {
  const csv = pythonCsv({ query: "" });
  assert.ok(csv.includes('"A ""quoted"", field"'));
  assert.ok(csv.includes('"\'\t+SUM(1,2)"'));
  assert.ok(csv.includes("Café and emoji 🚀"));
  assert.ok(csv.endsWith("\r\n"));
});

test("real catalog search and CSV order agree for technical queries and filters", () => {
  const source = JSON.parse(readFileSync(join(ROOT, "data/resources.json"), "utf8"));
  for (const filters of [
    { query: "" },
    { query: "C" },
    { query: "C++" },
    { query: "C#" },
    { query: "cpp-msvc" },
    { query: "machine learning" },
    { query: "java", category: "programming-languages" },
    { query: "", category: "programming-languages", kind: "official-docs" },
    { query: "C++ impossible-query" },
  ]) {
    assert.equal(pythonCsv(filters, source), resourcesToCsv(searchResources(source, filters)),
      JSON.stringify(filters));
  }
});

test("Unicode and punctuation ties use the same deterministic ordering", () => {
  const source = [
    ["b", "Éclair"], ["z", "Zoo"], ["a", "éclair"],
    ["cpp", "C++"], ["c", "C"], ["sharp", "C#"],
    ["street", "Straße"], ["sigma", "Σίγμα"], ["astral", "𐐀 title"],
  ].map(([id, name]) => ({ ...base, id, name, summary: "A useful reference" }));
  for (const query of ["", "C", "C++", "C#", "eclair", "straße", "Σίγμα", "𐐀"]) {
    const filters = { query };
    assert.equal(pythonCsv(filters, source), resourcesToCsv(searchResources(source, filters)), query);
  }
});
