import test from "node:test";
import assert from "node:assert/strict";
import {
  normalizeText, searchResources, parseFilters, filtersToQuery, countBy,
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
