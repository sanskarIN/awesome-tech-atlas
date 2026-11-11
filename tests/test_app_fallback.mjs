import test from "node:test";
import assert from "node:assert/strict";

test("unavailable catalog reveals a useful local Markdown fallback", async () => {
  const previous = {
    document: globalThis.document,
    fetch: globalThis.fetch,
    window: globalThis.window,
    catalog: globalThis.__ATLAS_EMBEDDED_CATALOG__,
  };
  const fallback = { hidden: true };
  const status = { textContent: "Loading local catalog…" };
  let cardsCleared = false;
  const controls = {
    "#query": { disabled: true },
    "#category": { disabled: true },
    "#kind": { disabled: true },
    "#clear-filters": { disabled: true },
    "#results-status": status,
    "#cards": { replaceChildren() { cardsCleared = true; } },
    "#empty": { hidden: true },
    "#load-fallback": fallback,
    "#total-count": { textContent: "" },
    "#category-count": { textContent: "" },
  };
  try {
    globalThis.document = {
      baseURI: "http://127.0.0.1:8000/site/",
      querySelector(selector) {
        assert.ok(Object.hasOwn(controls, selector), "unknown selector: " + selector);
        return controls[selector];
      },
    };
    globalThis.window = { location: { protocol: "http:" } };
    globalThis.fetch = async () => { throw new Error("simulated offline request"); };
    delete globalThis.__ATLAS_EMBEDDED_CATALOG__;

    await import("../site/app.mjs?test-catalog-load-failure");
    await new Promise((resolve) => setImmediate(resolve));

    assert.equal(fallback.hidden, false);
    assert.match(status.textContent, /Could not load the local JSON catalog/);
    assert.match(status.textContent, /simulated offline request/);
    assert.equal(cardsCleared, true);
    assert.equal(controls["#query"].disabled, true);
  } finally {
    globalThis.document = previous.document;
    globalThis.fetch = previous.fetch;
    globalThis.window = previous.window;
    globalThis.__ATLAS_EMBEDDED_CATALOG__ = previous.catalog;
  }
});
