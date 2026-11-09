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
    assert.equal(resources.length, 30);
    assert.ok(resources.some((r) => r.id === "rust"));
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
