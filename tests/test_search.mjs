import test from "node:test";
import assert from "node:assert/strict";
import {
  normalizeText, searchResources, parseFilters, filtersToQuery, countBy, resourcesToCsv,
  parseComparison, sanitizeComparisonIds,
} from "../site/search.mjs";

const records = [
  {
    id: "python", name: "Python documentation",
    subcategory: "Python language", summary: "A friendly scripting guide",
    category: "programming-languages", kind: "official-docs",
  },
  {
    id: "rust", name: "The Rust Programming Language",
    subcategory: "Rust language", summary: "A systems programming guide",
    category: "programming-languages", kind: "official-guide",
  },
  {
    id: "react", name: "React Learn",
    subcategory: "UI library", summary: "Interactive interfaces",
    category: "web-development", kind: "official-guide",
  },
];

test("normalization is case and accent insensitive", () => {
  assert.equal(normalizeText("Café / Scikit-Learn!"), "cafe scikit learn");
  assert.equal(normalizeText("RUST & Python"), "rust python");
});

test("search supports multi-token AND semantics and title ranking", () => {
  assert.deepEqual(searchResources(records, { query: "Rust" }).map((x) => x.id), ["rust"]);
  assert.deepEqual(searchResources(records, { query: "rust absent" }), []);
  assert.deepEqual(searchResources(records, { query: "programming" }).map((x) => x.id), ["rust", "python"]);
});

test("category and kind filters combine with search", () => {
  assert.deepEqual(
    searchResources(records, { category: "programming-languages", kind: "official-guide" })
      .map((x) => x.id),
    ["rust"],
  );
  assert.deepEqual(searchResources(records, { category: "invalid" }), []);
});

test("URL filter state is round-trippable and omits defaults", () => {
  const filters = { query: "rust ownership", category: "programming-languages", kind: "" };
  assert.deepEqual(parseFilters(filtersToQuery(filters)), filters);
  assert.equal(filtersToQuery({ query: "", category: "", kind: "" }), "");
  assert.equal(parseFilters("?q=" + "x".repeat(140)).query.length, 120);
});

test("counts are deterministic and grouped", () => {
  assert.deepEqual(countBy(records, "category"), [
    ["programming-languages", 2],
    ["web-development", 1],
  ]);
});

test("search never changes the source dataset", () => {
  const before = JSON.stringify(records);
  searchResources(records, { query: "rust" });
  assert.equal(JSON.stringify(records), before);
});

test("CSV export keeps ranking, deterministic field order and matching subset", () => {
  const selected = searchResources(records, { query: "programming", category: "programming-languages" });
  const csv = resourcesToCsv(selected);
  const lines = csv.trimEnd().split("\r\n");
  assert.equal(lines.length, 3);
  assert.equal(lines[0], '"id","name","category","subcategory","kind","summary","url","verified_on"');
  assert.ok(lines[1].startsWith('"rust",'));
  assert.ok(lines[2].startsWith('"python",'));
  assert.equal(resourcesToCsv(selected), csv);
  assert.equal(resourcesToCsv([]).trimEnd().split("\r\n").length, 1);
});

test("CSV export escapes quotes and neutralizes spreadsheet formulas", () => {
  const risky = {
    id: "example", name: '=HYPERLINK("https://example.org")',
    category: "web-development", subcategory: 'A "quoted", section',
    kind: "official-docs", summary: "\t+SUM(1,2)",
    url: "https://example.org", verified_on: "2026-11-08",
  };
  const csv = resourcesToCsv([risky]);
  assert.ok(csv.includes('"\'=HYPERLINK(""https://example.org"")"'));
  assert.ok(csv.includes('"A ""quoted"", section"'));
  assert.ok(csv.includes("\"'\t+SUM(1,2)\""));
  assert.ok(csv.endsWith("\r\n"));
});

test("comparison IDs are deduplicated, validated against the catalog and capped at three", () => {
  assert.deepEqual(sanitizeComparisonIds(
    ["rust", "rust", "deleted", "react", "python", "bad/id", "rust"],
    records,
  ), ["rust", "react", "python"]);
  assert.deepEqual(parseComparison("?compare=rust,unknown,react,rust,bad%2Fid,python,extra", records),
    ["rust", "react", "python"]);
  assert.deepEqual(parseComparison("?compare=__proto__,constructor", records), []);
  assert.deepEqual(parseComparison("?compare=", records), []);
});

test("comparison share links round-trip with filters without changing search semantics", () => {
  const filters = { query: "guide", category: "programming-languages", kind: "" };
  const url = filtersToQuery(filters, ["rust", "python", "rust", "react", "invalid/id"]);
  assert.deepEqual(parseFilters(url), filters);
  assert.deepEqual(parseComparison(url, records), ["rust", "python", "react"]);
  assert.equal(filtersToQuery({ query: "", category: "", kind: "" }), "");
  assert.deepEqual(searchResources(records, filters).map((r) => r.id), ["python", "rust"]);
});

test("technical names and resource identifiers are searchable without punctuation collapse", () => {
  const template = records[0];
  const languages = [
    { ...template, id: "c-msvc", name: "C language" },
    { ...template, id: "cpp-msvc", name: "C++ reference", summary: "Native reference" },
    { ...template, id: "csharp", name: "C# guide" },
    { ...template, id: "rust", name: "Rust documentation" },
    { ...template, id: "cmake", name: "CMake tools" },
    { ...template, id: "interop", name: "Interop", summary: "Connects C and C++ APIs" },
  ].map((item) => ({ ...item, subcategory: "Language tooling" }));
  for (const [query, expected] of [
    ["C", ["c-msvc", "interop"]],
    ["C++", ["cpp-msvc", "interop"]],
    ["C#", ["csharp"]],
    ["cpp-msvc", ["cpp-msvc"]],
    ["c++ guide", []],
  ]) {
    assert.deepEqual(searchResources(languages, { query }).map((x) => x.id), expected, query);
  }
  assert.equal(normalizeText("C++ / C# / C"), "c++ c# c");
  assert.equal(normalizeText("C++17"), "c++ 17");
  for (const query of ["C++", "C#", "C++ reference"]) {
    assert.equal(parseFilters(filtersToQuery({ query })).query, query);
  }
});

test("tie ordering uses lowercase code points and then resource ID", () => {
  const entries = [
    ["b", "Éclair"], ["z", "Zoo"], ["a", "éclair"], ["cpp", "C++"], ["c", "C"],
  ].map(([id, name]) => ({ ...records[0], id, name }));
  assert.deepEqual(searchResources(entries).map((x) => x.id), ["c", "cpp", "z", "a", "b"]);
});
