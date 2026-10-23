import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawn } from "node:child_process";
const state = mkdtempSync(join(tmpdir(), "virtualwago-browser-"));
const child = spawn(
  resolve("../target/debug/virtualwago-workbench"),
  ["--port", "18787", "--state-dir", state],
  { stdio: "inherit" },
);
const cleanup = () => {
  child.kill("SIGINT");
};
process.on("SIGINT", cleanup);
process.on("SIGTERM", cleanup);
child.on("exit", (code) => {
  rmSync(state, { recursive: true, force: true });
  process.exit(code ?? 1);
});
