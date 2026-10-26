"use strict";
const assert = require("node:assert/strict");
const {test} = require("node:test");
const path = require("node:path");
const {fileURLToPath, pathToFileURL} = require("node:url");
const {openRegisteredDiff} = require("../runtime/local_web/vscode/extension.js");

const root = path.resolve("bridge repo 中文");
const source = path.join(root, "a & 中文.dart");
const before = new URL("git:" + pathToFileURL(source).pathname);
before.search = JSON.stringify({path: source, ref: "a".repeat(40)});
const request = {repo: pathToFileURL(root).href, before: before.href, after: pathToFileURL(source).href};

function fixture({registered = root, readable = true, commandFails = false} = {}) {
  const calls = [];
  const vscode = {
    Uri: {parse(value) {
      const uri = new URL(value);
      return {scheme: uri.protocol.slice(0, -1), query: decodeURIComponent(uri.search.slice(1)),
        fsPath: uri.protocol === "file:" ? fileURLToPath(uri) : source};
    }},
    extensions: {getExtension() {
      return {activate: async () => ({getAPI: () => ({getRepository: () =>
        registered ? {rootUri: {fsPath: registered}} : null})})};
    }},
    workspace: {async openTextDocument(uri) {
      calls.push(["read", uri]);
      if (!readable) throw new Error("Repository not found");
    }},
    commands: {async executeCommand(...args) {
      calls.push(["open", ...args]);
      if (commandFails) throw new Error("Editor dispatch failed");
    }},
  };
  return {vscode, calls};
}

test("registered window reads its Git baseline and opens in that same window", async () => {
  const {vscode, calls} = fixture();
  assert.equal(await openRegisteredDiff(vscode, request), true);
  assert.deepEqual(calls.map(call => call[0]), ["read", "open"]);
  assert.equal(calls[1][1], "vscode.diff");
  assert.equal(calls[1][2].scheme, "git");
  assert.equal(calls[1][3].scheme, "file");
});

test("an unregistered repository declines before reading or opening", async () => {
  const {vscode, calls} = fixture({registered: null});
  assert.equal(await openRegisteredDiff(vscode, request), false);
  assert.deepEqual(calls, []);
});

test("a registered parent cannot stand in for the requested worktree", async () => {
  const {vscode, calls} = fixture({registered: path.dirname(root)});
  assert.equal(await openRegisteredDiff(vscode, request), false);
  assert.deepEqual(calls, []);
});

test("unreadable Git baseline safely declines without opening a diff", async () => {
  const {vscode, calls} = fixture({readable: false});
  assert.equal(await openRegisteredDiff(vscode, request), false);
  assert.deepEqual(calls.map(call => call[0]), ["read"]);
});

test("unavailable Git extension declines without opening", async () => {
  const {vscode, calls} = fixture();
  vscode.extensions.getExtension = () => undefined;
  assert.equal(await openRegisteredDiff(vscode, request), false);
  assert.deepEqual(calls, []);
});

test("a failed editor command is not reported as a safe fallback", async () => {
  const {vscode, calls} = fixture({commandFails: true});
  await assert.rejects(openRegisteredDiff(vscode, request), /Editor dispatch failed/);
  assert.deepEqual(calls.map(call => call[0]), ["read", "open"]);
});

test("invalid protocols and out-of-repository baseline paths are rejected", async () => {
  const {vscode, calls} = fixture();
  await assert.rejects(openRegisteredDiff(vscode, {...request, before: request.after}), /Invalid diff URI/);
  const outside = new URL(request.before);
  outside.search = JSON.stringify({path: path.join(path.dirname(root), "outside.dart"), ref: "a".repeat(40)});
  await assert.rejects(openRegisteredDiff(vscode, {...request, before: outside.href}), /outside the repository/);
  assert.deepEqual(calls, []);
});

const fs = require("node:fs");
const os = require("node:os");
const http = require("node:http");
const Module = require("node:module");
const {activate} = require("../runtime/local_web/vscode/extension.js");

test("focused-window discovery, authentication and descriptor ownership use the real listener", async () => {
  const testRoot = fs.realpathSync(os.tmpdir());
  const directory = fs.mkdtempSync(path.join(testRoot, "smartkit-vscode-"));
  const previousHome = os.homedir;
  const previousLocal = process.env.LOCALAPPDATA;
  const previousState = process.env.XDG_STATE_HOME;
  os.homedir = () => directory;
  process.env.LOCALAPPDATA = directory;
  process.env.XDG_STATE_HOME = directory;
  const base = process.platform === "darwin"
    ? path.join(directory, "Library", "Application Support") : directory;
  const descriptor = path.join(base, "smartkit", "local-web", "vscode-bridge.json");
  const contexts = [];
  function startWindow(focused) {
    const f = fixture({registered: null});
    let focus;
    f.vscode.window = {
      state: {focused},
      onDidChangeWindowState(callback) {
        focus = callback;
        return {dispose() {}};
      },
    };
    const context = {subscriptions: []};
    contexts.push(context);
    const previousLoad = Module._load;
    Module._load = function(name, ...args) {
      return name === "vscode" ? f.vscode : previousLoad.call(this, name, ...args);
    };
    try { activate(context); } finally { Module._load = previousLoad; }
    return {...f, focus() {
      f.vscode.window.state.focused = true;
      focus({focused: true});
    }, dispose() {
      for (const item of context.subscriptions.splice(0)) item.dispose();
    }};
  }
  async function waitFor(predicate) {
    const deadline = Date.now() + 3000;
    while (!predicate()) {
      assert.ok(Date.now() < deadline, "bridge did not become ready");
      await new Promise(resolve => setTimeout(resolve, 5));
    }
  }
  const read = () => JSON.parse(fs.readFileSync(descriptor, "utf8"));
  const send = (state, headers = {}) => new Promise((resolve, reject) => {
    const content = JSON.stringify(request);
    const sent = http.request({
      hostname: "127.0.0.1", port: state.port, path: "/diff", method: "POST",
      headers: {"Authorization": "Bearer " + state.token,
        "Content-Type": "application/json", "Content-Length": Buffer.byteLength(content), ...headers},
    }, response => {
      let body = "";
      response.setEncoding("utf8");
      response.on("data", part => body += part);
      response.on("end", () => resolve({status: response.statusCode, body: JSON.parse(body)}));
    });
    sent.on("error", reject);
    sent.end(content);
  });
  try {
    const first = startWindow(true);
    await waitFor(() => fs.existsSync(descriptor));
    const one = read();
    const second = startWindow(false);
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(read().token, one.token);
    second.focus();
    await waitFor(() => read().token !== one.token);
    const two = read();
    assert.match(two.token, /^[0-9a-f]{64}$/);
    assert.equal((await send(two, {Authorization: "Bearer wrong"})).status, 401);
    assert.equal((await send(two, {Origin: "http://untrusted.example"})).status, 401);
    assert.deepEqual(await send(two), {status: 200, body: {status: "fallback"}});
    assert.deepEqual(second.calls, []);
    const registered = fixture();
    second.vscode.extensions = registered.vscode.extensions;
    assert.deepEqual(await send(two), {status: 200, body: {status: "opened"}});
    assert.deepEqual(second.calls.map(call => call[0]), ["read", "open"]);
    assert.deepEqual(first.calls, []);
    first.dispose();
    assert.equal(read().token, two.token);
    second.dispose();
    assert.equal(fs.existsSync(descriptor), false);
  } finally {
    for (const context of contexts) {
      for (const item of context.subscriptions.splice(0)) item.dispose();
    }
    os.homedir = previousHome;
    if (previousLocal === undefined) delete process.env.LOCALAPPDATA;
    else process.env.LOCALAPPDATA = previousLocal;
    if (previousState === undefined) delete process.env.XDG_STATE_HOME;
    else process.env.XDG_STATE_HOME = previousState;
    const resolved = fs.realpathSync(directory);
    assert.equal(path.dirname(resolved), testRoot);
    fs.rmSync(resolved, {recursive: true, force: true});
  }
});
