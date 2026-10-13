// Starts the web app: node scripts/run_web.mjs [backend|frontend|all]
// (used by `npm run backend`, `npm run frontend` and `npm run dev`).
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const which = process.argv[2] ?? "all";
const windows = process.platform === "win32";
const python = [join(root, ".venv", "Scripts", "python.exe"), join(root, ".venv", "bin", "python")].find(existsSync);

if (which !== "frontend" && !python) {
  console.error("No .venv found. Set up the generator first (see README: python scripts/setup.py).");
  process.exit(1);
}
if (which !== "backend" && !existsSync(join(root, "frontend", "node_modules"))) {
  console.error("Frontend dependencies missing. Run: npm run setup");
  process.exit(1);
}

const children = [];
function start(name, command, args, cwd, color) {
  // npm is a .cmd script on Windows, so it needs a shell (fixed arguments only).
  const viaShell = windows && command === "npm";
  const child = viaShell
    ? spawn([command, ...args].join(" "), { cwd, shell: true, env: process.env })
    : spawn(command, args, { cwd, env: process.env });
  const prefix = `\x1b[${color}m[${name}]\x1b[0m `;
  const pipe = (stream, out) =>
    stream.on("data", (chunk) => {
      for (const line of chunk.toString().split(/\r?\n/)) if (line.trim()) out.write(prefix + line + "\n");
    });
  pipe(child.stdout, process.stdout);
  pipe(child.stderr, process.stderr);
  child.on("exit", (code) => {
    console.log(`${prefix}exited (${code ?? "signal"})`);
    for (const other of children) if (other !== child && other.exitCode === null) other.kill();
    process.exitCode = code ?? 0;
  });
  children.push(child);
}

if (which === "backend" || which === "all") {
  start("api", python, ["-m", "backend"], root, "36");
  console.log("\x1b[36m[api]\x1b[0m http://127.0.0.1:8765 (docs: /api/docs)");
}
if (which === "frontend" || which === "all") {
  start("web", "npm", ["run", "dev"], join(root, "frontend"), "35");
}
process.on("SIGINT", () => children.forEach((c) => c.kill()));
