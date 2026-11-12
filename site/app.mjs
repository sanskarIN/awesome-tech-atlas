import {
  countBy, filtersToQuery, parseFilters, resourcesToCsv, searchResources,
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
const exportButton = document.querySelector("#export-results");
const status = document.querySelector("#results-status");
const cards = document.querySelector("#cards");
const empty = document.querySelector("#empty");
const loadFallback = document.querySelector("#load-fallback");
const totalCount = document.querySelector("#total-count");
const categoryCount = document.querySelector("#category-count");
let entries = [];
const offlineProfiles = globalThis.__ATLAS_EMBEDDED_PROFILES__;

function hasOfflineProfile(id) {
  return offlineProfiles !== null
    && typeof offlineProfiles === "object"
    && Object.hasOwn(offlineProfiles, id)
    && typeof offlineProfiles[id] === "string";
}

function openOfflineProfile(record) {
  if (!hasOfflineProfile(record.id)) return;
  const dialog = document.querySelector("#offline-profile-dialog");
  const heading = document.querySelector("#offline-profile-title");
  const markdown = document.querySelector("#offline-profile-markdown");
  const githubLink = document.querySelector("#offline-profile-github");
  const download = document.querySelector("#download-profile-markdown");

  heading.textContent = record.name;
  markdown.textContent = offlineProfiles[record.id];
  githubLink.href = GITHUB_PROFILES + encodeURIComponent(record.id) + ".md";
  download.onclick = () => {
    const blob = new Blob([offlineProfiles[record.id]], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = record.id + ".md";
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  };
  dialog.showModal();
}

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
  if (hasOfflineProfile(record.id)) {
    const profileButton = el("button", "profile-link offline-profile-trigger", record.name);
    profileButton.type = "button";
    profileButton.addEventListener("click", () => openOfflineProfile(record));
    heading.append(profileButton);
  } else {
    const profileLink = el("a", "profile-link", record.name);
    profileLink.href = GITHUB_PROFILES + encodeURIComponent(record.id) + ".md";
    heading.append(profileLink);
  }

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
    + " curated resources.";
  clearButton.disabled = !(filters.query || filters.category || filters.kind);
  exportButton.disabled = matched.length === 0;

  // file:// snapshots cannot reliably modify history; filtering still works locally.
  if (updateUrl && window.location.protocol !== "file:" && window.history?.replaceState) {
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
    // A generated offline snapshot embeds a validated catalog, so file:// needs no fetch.
    // The repository version still loads the canonical JSON from the local server.
    let data;
    if (Array.isArray(globalThis.__ATLAS_EMBEDDED_CATALOG__)) {
      data = globalThis.__ATLAS_EMBEDDED_CATALOG__;
    } else {
      const response = await fetch(new URL("../data/resources.json", document.baseURI), {
        credentials: "omit",
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Catalog request returned HTTP " + response.status);
      data = await response.json();
    }
    if (!Array.isArray(data) || data.some((entry) => !validRecord(entry))) {
      throw new Error("Catalog shape is invalid; run the repository validator.");
    }
    if (new Set(data.map((item) => item.id)).size !== data.length) {
      throw new Error("Catalog contains duplicate IDs.");
    }

    entries = data;
    loadFallback.hidden = true;
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
    exportButton.addEventListener("click", () => {
      const matched = searchResources(entries, currentFilters());
      if (matched.length === 0) return;
      const blob = new Blob(["\uFEFF", resourcesToCsv(matched)], {
        type: "text/csv;charset=utf-8",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "awesome-tech-atlas-results.csv";
      anchor.click();
      setTimeout(() => URL.revokeObjectURL(url), 0);
    });
    document.querySelector("#offline-profile-close").addEventListener("click", () => {
      document.querySelector("#offline-profile-dialog").close();
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
    loadFallback.hidden = false;
    status.textContent = "Could not load the local JSON catalog. Run a local HTTP server from the repository root, then open /site/. "
      + (error instanceof Error ? error.message : "");
    cards.replaceChildren();
  }
}

initialize();
