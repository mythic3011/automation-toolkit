const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const { spawnSync } = require("node:child_process");

const packageDir = path.resolve(__dirname, "..");
const distDir = path.join(packageDir, "dist");

function runBuild(mode) {
  const result = spawnSync(process.execPath, ["build/build.js"], {
    cwd: packageDir,
    encoding: "utf8",
    env: { ...process.env, BUILD_MODE: mode },
  });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
}

function browserFixture() {
  const listeners = {};
  const window = {
    location: { href: "https://example.invalid/" },
    fetch: () => Promise.resolve({}),
  };
  class XMLHttpRequest {
    open() {}
    send() {}
  }
  const document = {
    readyState: "loading",
    body: {},
    title: "Smoke test",
    addEventListener(name, callback) {
      listeners[name] = callback;
    },
    getElementById() {
      return null;
    },
  };
  const context = vm.createContext({
    window,
    document,
    XMLHttpRequest,
    console: { log() {}, warn() {}, error() {} },
    setTimeout() {
      return 1;
    },
    clearTimeout() {},
    Date,
    Set,
    Map,
    URL,
  });
  return { context, listeners, window };
}

test("production build emits regular and minified userscripts", () => {
  runBuild("production");
  for (const filename of [
    "media-catcher.user.js",
    "media-catcher.min.user.js",
  ]) {
    const output = fs.readFileSync(path.join(distDir, filename), "utf8");
    assert.match(output, /^\/\/ ==UserScript==/);
    assert.match(output, /@run-at\s+document-end/);
    assert.match(output, /_mediaCatcherInstalled/);
  }
});

test("production userscripts start in a minimal browser context", () => {
  runBuild("production");
  for (const filename of [
    "media-catcher.user.js",
    "media-catcher.min.user.js",
  ]) {
    const output = fs.readFileSync(path.join(distDir, filename), "utf8");
    const fixture = browserFixture();

    assert.doesNotThrow(() => vm.runInContext(output, fixture.context));
    assert.equal(fixture.window._mediaCatcherInstalled, true);
    assert.equal(typeof fixture.listeners.DOMContentLoaded, "function");
  }
});

test("development build emits an executable development userscript", () => {
  runBuild("development");
  const filename = path.join(distDir, "media-catcher.dev.user.js");
  const output = fs.readFileSync(filename, "utf8");
  assert.match(output, /@version\s+2\.4\.0-dev/);
  const fixture = browserFixture();

  assert.doesNotThrow(() => vm.runInContext(output, fixture.context));
  assert.equal(fixture.window._mediaCatcherInstalled, true);
});

test("build rejects unsupported modes instead of silently making a dev build", () => {
  const result = spawnSync(process.execPath, ["build/build.js"], {
    cwd: packageDir,
    encoding: "utf8",
    env: { ...process.env, BUILD_MODE: "staging" },
  });

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /BUILD_MODE must be production or development/);
});
