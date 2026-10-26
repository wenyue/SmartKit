"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");

function samePath(left, right) {
  const normalize = value => {
    const result = path.resolve(value);
    return process.platform === "win32" ? result.toLowerCase() : result;
  };
  return normalize(left) === normalize(right);
}

async function openRegisteredDiff(vscode, request) {
  if (!request || typeof request !== "object" ||
      !["repo", "before", "after"].every(key => typeof request[key] === "string")) {
    throw new Error("Invalid diff request");
  }
  const repo = vscode.Uri.parse(request.repo);
  const before = vscode.Uri.parse(request.before);
  const after = vscode.Uri.parse(request.after);
  if (repo.scheme !== "file" || before.scheme !== "git" || after.scheme !== "file") {
    throw new Error("Invalid diff URI");
  }
  const history = JSON.parse(before.query);
  if (typeof history.path !== "string" || typeof history.ref !== "string" ||
      !/^(?:[0-9a-f]{40}|[0-9a-f]{64})$/.test(history.ref)) {
    throw new Error("Invalid Git baseline");
  }
  const relative = path.relative(repo.fsPath, history.path);
  if (!relative || path.isAbsolute(relative) || relative === ".." ||
      relative.startsWith(".." + path.sep)) {
    throw new Error("Git baseline is outside the repository");
  }
  try {
    const extension = vscode.extensions.getExtension("vscode.git");
    if (!extension) return false;
    const git = (await extension.activate()).getAPI(1);
    const registered = git.getRepository(repo);
    // A parent repository is not registration of a linked worktree.
    if (!registered || !samePath(registered.rootUri.fsPath, repo.fsPath)) return false;
    await vscode.workspace.openTextDocument(before);
  } catch {
    // No diff was opened: the verified fixed blob can safely be materialized instead.
    return false;
  }
  // Keep the capability check, read and open in this same window.
  // Command failures propagate; retrying them could open a duplicate editor.
  await vscode.commands.executeCommand("vscode.diff", before, after);
  return true;
}

function stateFile() {
  let base;
  if (process.platform === "darwin") {
    base = path.join(os.homedir(), "Library", "Application Support");
  } else {
    const configured = process.platform === "win32"
      ? process.env.LOCALAPPDATA : process.env.XDG_STATE_HOME;
    base = configured && path.isAbsolute(configured) ? configured
      : path.join(os.homedir(), ...(process.platform === "win32"
        ? ["AppData", "Local"] : [".local", "state"]));
  }
  fs.mkdirSync(base, {recursive: true, mode: 0o700});
  let directory = fs.realpathSync(base);
  for (const name of ["smartkit", "local-web"]) {
    directory = path.join(directory, name);
    try {
      if (fs.lstatSync(directory).isSymbolicLink()) throw new Error("Bridge state redirects");
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
      fs.mkdirSync(directory, {mode: 0o700});
    }
  }
  return path.join(directory, "vscode-bridge.json");
}

function checkStateFile(file) {
  try {
    if (fs.lstatSync(file).isSymbolicLink()) throw new Error("Bridge state redirects");
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
}

function activate(context) {
  const vscode = require("vscode");
  const token = crypto.randomBytes(32).toString("hex");
  const file = stateFile();
  let disposed = false;
  const reply = (response, status, value) => {
    if (response.destroyed || response.writableEnded) return;
    response.writeHead(status, {"Content-Type": "application/json", "Cache-Control": "no-store"});
    response.end(JSON.stringify(value));
  };
  const server = http.createServer(async (request, response) => {
    // Browsers cannot invoke this private loopback capability.
    const supplied = Buffer.from(request.headers.authorization || "");
    const expected = Buffer.from("Bearer " + token);
    if (request.headers.origin || supplied.length !== expected.length ||
        !crypto.timingSafeEqual(supplied, expected)) {
      reply(response, 401, {});
      return;
    }
    if (request.method !== "POST" || request.url !== "/diff" || disposed) {
      reply(response, 404, {});
      return;
    }
    const chunks = [];
    try {
      let size = 0;
      for await (const chunk of request) {
        size += chunk.length;
        if (size > 65536) {
          reply(response, 413, {});
          return;
        }
        chunks.push(chunk);
      }
      const opened = await openRegisteredDiff(vscode, JSON.parse(Buffer.concat(chunks).toString("utf8")));
      reply(response, 200, {status: opened ? "opened" : "fallback"});
    } catch (error) {
      // Final request ownership: report the failure, without claiming a safe editor retry.
      console.error("SmartKit diff bridge could not complete a request:", error);
      reply(response, 500, {status: "failed"});
    }
  });
  server.requestTimeout = 10000;
  server.headersTimeout = 10000;
  server.on("error", error => console.error("SmartKit diff bridge is unavailable:", error));
  function publish() {
    const address = server.address();
    if (disposed || !address || !vscode.window.state.focused) return;
    const temporary = file + "." + token + ".pending";
    try {
      checkStateFile(file);
      fs.writeFileSync(temporary, JSON.stringify({protocol: 1, port: address.port, token}),
        {mode: 0o600, flag: "wx"});
      fs.renameSync(temporary, file);
    } finally {
      try { fs.unlinkSync(temporary); } catch (error) {
        if (error.code !== "ENOENT") throw error;
      }
    }
  }
  const publishSafely = () => {
    try { publish(); } catch (error) {
      console.error("SmartKit diff bridge could not advertise its window:", error);
    }
  };
  server.listen(0, "127.0.0.1", publishSafely);
  context.subscriptions.push(vscode.window.onDidChangeWindowState(state => {
    if (state.focused) publishSafely();
  }), {dispose() {
    disposed = true;
    server.close();
    try {
      checkStateFile(file);
      // Another focused window may have replaced this descriptor.
      if (JSON.parse(fs.readFileSync(file, "utf8")).token === token) fs.unlinkSync(file);
    } catch (error) {
      if (error.code !== "ENOENT") console.error("SmartKit diff bridge cleanup failed:", error);
    }
  }});
}

module.exports = {activate, openRegisteredDiff};
