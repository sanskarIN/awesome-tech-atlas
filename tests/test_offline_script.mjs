import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Script } from "node:vm";

test("generated offline script is valid classic JavaScript with embedded catalog", () => {
  const directory = mkdtempSync(join(tmpdir(), "atlas-offline-"));
  try {
    const output = join(directory, "atlas.html");
    execFileSync("python3", ["scripts/build_offline.py", "--output", output], {
      cwd: process.cwd(), encoding: "utf8",
    });
    const html = readFileSync(output, "utf8");
    const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
    assert.equal(scripts.length, 1, "offline page must have exactly one inline script");
    assert.doesNotMatch(html, /<script[^>]*src=/i);
    assert.doesNotMatch(html, /<link[^>]*rel="stylesheet"/i);
    assert.doesNotMatch(scripts[0][1], /\bimport\.meta\b/);
    assert.doesNotThrow(() => new Script(scripts[0][1]));
    const data = scripts[0][1].match(/globalThis\.__ATLAS_EMBEDDED_CATALOG__ = (\[[^\n]+\]);/);
    assert.ok(data, "expected embedded JSON assignment");
    const resources = JSON.parse(data[1]);
    const expected = JSON.parse(readFileSync(new URL("../data/resources.json", import.meta.url), "utf8"));
    assert.ok(expected.length > 0);
    assert.deepEqual(resources, expected);
    for (const id of ["crafting-interpreters", "gdb", "wai-tutorials", "opentelemetry", "cmake-tutorial", "mdn-webassembly", "openssf-scorecard"]) {
      assert.ok(resources.some((entry) => entry.id === id), `missing ${id}`);
    }
    assert.ok(resources.some((r) => r.id === "rust"));
    assert.match(html, /id="comparison-table"/);
    assert.match(scripts[0][1], /function parseComparison\(/);
    assert.match(scripts[0][1], /function renderComparison\(/);
    const profileAssignment = scripts[0][1].match(
      /globalThis\.__ATLAS_EMBEDDED_PROFILES__ = (\{[^\n]+\});/,
    );
    assert.ok(profileAssignment, "expected full embedded resource profiles");
    const profiles = JSON.parse(profileAssignment[1]);
    assert.deepEqual(Object.keys(profiles).sort(), resources.map((entry) => entry.id).sort());
    for (const entry of resources) {
      const source = readFileSync(new URL(`../resources/${entry.id}.md`, import.meta.url), "utf8");
      assert.equal(profiles[entry.id], source, `embedded profile differs: ${entry.id}`);
    }
    assert.ok(profiles.rust.includes("## Worked example"));
    assert.equal(typeof profiles.python, "string");
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
