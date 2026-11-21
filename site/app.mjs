import {
  countBy, filtersToQuery, parseComparison, parseFilters, resourcesToCsv,
  sanitizeComparisonIds, searchResources,
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
const compareStatus = document.querySelector("#compare-status");
const comparePanel = document.querySelector("#compare-panel");
const compareTable = document.querySelector("#comparison-table");
const clearComparison = document.querySelector("#clear-comparison");
let entries = [];
let selectedIds = [];
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
  const compare = el("button", "compare-toggle");
  compare.type = "button";
  compare.dataset.compareId = record.id;
  compare.addEventListener("click", () => toggleComparison(record.id));
  article.append(heading, meta, description, footer, compare);
  return article;
}


function updateComparisonControls() {
  const full = selectedIds.length === 3;
  for (const button of cards.querySelectorAll(".compare-toggle")) {
    const id = button.dataset.compareId;
    const chosen = selectedIds.includes(id);
    const record = entries.find((item) => item.id === id);
    button.disabled = full && !chosen;
    button.setAttribute("aria-pressed", String(chosen));
    button.textContent = chosen ? "Remove from comparison" : "Add to comparison";
    button.setAttribute("aria-label", (chosen ? "Remove " : "Compare ") + record.name);
    button.title = full && !chosen ? "Remove one of the three selected resources first" : "";
  }
}

function renderComparison() {
  const chosen = selectedIds.map((id) => entries.find((record) => record.id === id));
  compareStatus.textContent = selectedIds.length + " of 3 resources selected for comparison.";
  clearComparison.disabled = selectedIds.length === 0;
  comparePanel.hidden = selectedIds.length === 0;
  compareTable.replaceChildren();
  if (!chosen.length) return;

  const head = el("thead");
  const headerRow = el("tr");
  const corner = el("th", "", "Attribute");
  corner.scope = "col";
  headerRow.append(corner);
  for (const record of chosen) {
    const cell = el("th");
    cell.scope = "col";
    cell.append(el("span", "comparison-name", record.name));
    const remove = el("button", "comparison-remove", "Remove");
    remove.type = "button";
    remove.setAttribute("aria-label", "Remove " + record.name + " from comparison");
    remove.addEventListener("click", () => {
      toggleComparison(record.id);
      compareStatus.focus();
    });
    cell.append(remove);
    headerRow.append(cell);
  }
  head.append(headerRow);

  const body = el("tbody");
  const fields = [
    ["Topic", (record) => labelFor(record.category)],
    ["Subcategory", (record) => record.subcategory],
    ["Resource type", (record) => record.kind.replaceAll("-", " ")],
    ["Curated summary", (record) => record.summary],
    ["Official source", (record) => {
      const link = el("a", "", "Open upstream source");
      link.href = record.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.referrerPolicy = "no-referrer";
      return link;
    }],
    ["Last source inspection", (record) => record.verified_on],
    ["Curated profile", (record) => {
      if (hasOfflineProfile(record.id)) {
        const button = el("button", "comparison-profile", "Read offline profile");
        button.type = "button";
        button.addEventListener("click", () => openOfflineProfile(record));
        return button;
      }
      const link = el("a", "", "Read full profile");
      link.href = GITHUB_PROFILES + encodeURIComponent(record.id) + ".md";
      return link;
    }],
  ];
  for (const [label, getValue] of fields) {
    const tr = el("tr");
    const th = el("th", "comparison-row-heading", label);
    th.scope = "row";
    tr.append(th);
    for (const record of chosen) {
      const td = el("td");
      const value = getValue(record);
      if (typeof value === "string") td.textContent = value;
      else td.append(value);
      tr.append(td);
    }
    body.append(tr);
  }
  compareTable.append(head, body);
}

function saveViewUrl() {
  // Standalone snapshots support comparisons without writing file:// history.
  if (window.location.protocol === "file:" || !window.history?.replaceState) return;
  const next = window.location.pathname
    + filtersToQuery(currentFilters(), selectedIds) + window.location.hash;
  window.history.replaceState(null, "", next);
}

function toggleComparison(id) {
  if (selectedIds.includes(id)) {
    selectedIds = selectedIds.filter((item) => item !== id);
  } else if (selectedIds.length < 3) {
    selectedIds = sanitizeComparisonIds([...selectedIds, id], entries);
  }
  updateComparisonControls();
  renderComparison();
  saveViewUrl();
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
  updateComparisonControls();
  renderComparison();

  if (updateUrl) saveViewUrl();
}

function restoreFromUrl() {
  const filters = parseFilters(window.location.search);
  selectedIds = parseComparison(window.location.search, entries);
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
    clearComparison.addEventListener("click", () => {
      selectedIds = [];
      updateComparisonControls();
      renderComparison();
      saveViewUrl();
      queryInput.focus();
    });
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
