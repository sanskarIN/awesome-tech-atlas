import {
  countBy, filtersToQuery, parseFilters, searchResources,
} from "./search.mjs";

const GITHUB_PROFILES = "https://github.com/sanskarIN/awesome-tech-atlas/blob/main/resources/";
const CATEGORIES = {
  "programming-languages": "Programming languages",
  "computer-science-fundamentals": "Computer science fundamentals",
  "artificial-intelligence-machine-learning": "AI & machine learning",
  "deep-learning-neural-networks": "Deep learning & neural networks",
  "software-engineering": "Software engineering",
  "systems-programming": "Systems programming",
  "compiler-development": "Compiler development",
  "operating-systems": "Operating systems",
  "databases-storage": "Databases & storage",
  "developer-tools": "Developer tools",
  "web-development": "Web development",
  "mobile-desktop-development": "Mobile & desktop development",
  "scientific-computing": "Scientific computing",
  "algorithms-data-structures": "Algorithms & data structures",
  "computer-architecture": "Computer architecture",
  "networking-distributed-systems": "Networking & distributed systems",
  "cybersecurity-secure-engineering": "Cybersecurity & secure engineering",
  "cloud-computing-devops": "Cloud computing & DevOps",
  "open-source-projects-communities": "Open source & communities",
};

const queryInput = document.querySelector("#query");
const categoryInput = document.querySelector("#category");
const kindInput = document.querySelector("#kind");
const clearButton = document.querySelector("#clear-filters");
const status = document.querySelector("#results-status");
const cards = document.querySelector("#cards");
const empty = document.querySelector("#empty");
const totalCount = document.querySelector("#total-count");
const categoryCount = document.querySelector("#category-count");
let entries = [];

function labelFor(key) {
  return CATEGORIES[key] ?? key.replaceAll("-", " ");
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function validRecord(record) {
  if (!record || typeof record !== "object") return false;
  for (const field of ["id", "name", "category", "kind", "subcategory", "summary", "url", "verified_on"]) {
    if (typeof record[field] !== "string") return false;
  }
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(record.id)) return false;
  try {
    const url = new URL(record.url);
    return url.protocol === "https:" && !url.username && !url.password;
  } catch {
    return false;
  }
}

function resourceCard(record) {
  const article = el("article", "resource-card");
  const heading = el("h3", "card-title");
  const profileLink = el("a", "profile-link", record.name);
  profileLink.href = GITHUB_PROFILES + encodeURIComponent(record.id) + ".md";
  heading.append(profileLink);

  const meta = el("div", "card-meta");
  meta.append(
    el("span", "category-pill", labelFor(record.category)),
    el("span", "kind-pill", record.kind.replaceAll("-", " ")),
  );

  const description = el("p", "card-description", record.summary);
  const footer = el("div", "card-footer");
  const upstream = el("a", "official-link", "Official source ↗");
  upstream.href = record.url;
  upstream.target = "_blank";
  upstream.rel = "noopener noreferrer";
  upstream.referrerPolicy = "no-referrer";

  const inspected = el("span", "inspected", "Source checked: " + record.verified_on);
  footer.append(upstream, inspected);
  article.append(heading, meta, description, footer);
  return article;
}

function populateSelect(select, counts, transform) {
  for (const [value, count] of counts) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = transform(value) + " (" + count + ")";
    select.append(option);
  }
}

function currentFilters() {
  return {
    query: queryInput.value.slice(0, 120),
    category: categoryInput.value,
    kind: kindInput.value,
  };
}

function render(updateUrl = true) {
  const filters = currentFilters();
  const matched = searchResources(entries, filters);
  const fragment = document.createDocumentFragment();
  for (const record of matched) fragment.append(resourceCard(record));
  cards.replaceChildren(fragment);

  empty.hidden = matched.length !== 0;
  status.textContent = "Showing " + matched.length + " of " + entries.length
    + " curated resources" + (matched.length === 1 ? "." : ".");
  clearButton.disabled = !(filters.query || filters.category || filters.kind);

  if (updateUrl && window.history?.replaceState) {
    const next = window.location.pathname + filtersToQuery(filters) + window.location.hash;
    window.history.replaceState(null, "", next);
  }
}

function restoreFromUrl() {
  const filters = parseFilters(window.location.search);
  queryInput.value = filters.query;
  categoryInput.value = [...categoryInput.options].some((opt) => opt.value === filters.category)
    ? filters.category : "";
  kindInput.value = [...kindInput.options].some((opt) => opt.value === filters.kind)
    ? filters.kind : "";
  render(false);
}

async function initialize() {
  try {
    const response = await fetch(new URL("../data/resources.json", import.meta.url), {
      credentials: "omit",
      cache: "no-store",
    });
    if (!response.ok) throw new Error("Catalog request returned HTTP " + response.status);
    const data = await response.json();
    if (!Array.isArray(data) || data.some((entry) => !validRecord(entry))) {
      throw new Error("Catalog shape is invalid; run the repository validator.");
    }
    if (new Set(data.map((item) => item.id)).size !== data.length) {
      throw new Error("Catalog contains duplicate IDs.");
    }

    entries = data;
    totalCount.textContent = String(entries.length);
    categoryCount.textContent = String(new Set(entries.map((r) => r.category)).size);
    populateSelect(categoryInput, countBy(entries, "category"), labelFor);
    populateSelect(kindInput, countBy(entries, "kind"), (value) => value.replaceAll("-", " "));

    for (const control of [queryInput, categoryInput, kindInput]) control.disabled = false;
    queryInput.addEventListener("input", () => render());
    categoryInput.addEventListener("change", () => render());
    kindInput.addEventListener("change", () => render());
    clearButton.addEventListener("click", () => {
      queryInput.value = "";
      categoryInput.value = "";
      kindInput.value = "";
      render();
      queryInput.focus();
    });
    window.addEventListener("popstate", restoreFromUrl);
    document.addEventListener("keydown", (event) => {
      const target = event.target;
      const editing = target instanceof HTMLElement &&
        (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
      if (event.key === "/" && !event.altKey && !event.ctrlKey && !event.metaKey && !editing) {
        event.preventDefault();
        queryInput.focus();
      }
      if (event.key === "Escape" && document.activeElement === queryInput && queryInput.value) {
        queryInput.value = "";
        render();
      }
    });
    restoreFromUrl();
  } catch (error) {
    status.textContent = "Could not load the local JSON catalog. Run a local HTTP server from the repository root, then open /site/. "
      + (error instanceof Error ? error.message : "");
    cards.replaceChildren();
  }
}

initialize();
