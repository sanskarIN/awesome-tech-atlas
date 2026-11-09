/**
 * Dependency-free, pure catalog search logic shared by the browser and tests.
 * The browser reads the existing repository JSON; no additional API is required.
 */
const FIELD_WEIGHTS = [
  ["name", 8],
  ["subcategory", 5],
  ["summary", 3],
  ["category", 2],
  ["kind", 1],
];

export function normalizeText(value) {
  const text = String(value ?? "")
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLowerCase();
  return (text.match(/[\p{L}\p{N}_]+/gu) ?? []).join(" ");
}

export function searchResources(records, filters = {}) {
  const query = String(filters.query ?? "");
  const category = String(filters.category ?? "");
  const kind = String(filters.kind ?? "");
  const tokens = normalizeText(query).split(" ").filter(Boolean);
  const matches = [];

  for (const entry of records) {
    if (category && entry.category !== category) continue;
    if (kind && entry.kind !== kind) continue;
    const fields = FIELD_WEIGHTS.map(([key, weight]) => [normalizeText(entry[key]), weight]);
    if (!tokens.every((token) => fields.some(([text]) => text.includes(token)))) continue;
    const score = tokens.reduce(
      (sum, token) => sum + Math.max(0, ...fields
        .filter(([text]) => text.includes(token))
        .map(([, weight]) => weight)),
      0,
    );
    matches.push({ entry, score });
  }

  matches.sort((a, b) => b.score - a.score
    || a.entry.name.toLowerCase().localeCompare(b.entry.name.toLowerCase(), "en")
    || a.entry.id.localeCompare(b.entry.id, "en"));
  return matches.map(({ entry }) => entry);
}

export function parseFilters(search) {
  const params = new URLSearchParams(search);
  return {
    query: (params.get("q") ?? "").slice(0, 120),
    category: (params.get("category") ?? "").slice(0, 80),
    kind: (params.get("kind") ?? "").slice(0, 80),
  };
}

export function filtersToQuery(filters) {
  const params = new URLSearchParams();
  if (filters.query?.trim()) params.set("q", filters.query.trim());
  if (filters.category) params.set("category", filters.category);
  if (filters.kind) params.set("kind", filters.kind);
  const result = params.toString();
  return result ? "?" + result : "";
}

export function countBy(records, field) {
  return [...records.reduce((counts, item) => {
    const value = item[field];
    counts.set(value, (counts.get(value) ?? 0) + 1);
    return counts;
  }, new Map()).entries()].sort(([a], [b]) => a.localeCompare(b, "en"));
}
