// Copy Monaco's prebuilt files into public/ so the code editor loads from
// this app instead of a CDN (works offline). Runs on npm install / dev / build.
import { cpSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = join(root, "node_modules", "monaco-editor", "min", "vs");
const target = join(root, "public", "monaco", "vs");
const stamp = join(root, "public", "monaco", "version.txt");
const version = JSON.parse(readFileSync(join(root, "node_modules", "monaco-editor", "package.json"), "utf8")).version;

if (existsSync(stamp) && readFileSync(stamp, "utf8") === version) process.exit(0);
cpSync(source, target, { recursive: true });
writeFileSync(stamp, version);
console.log(`monaco-editor ${version} copied to public/monaco/vs`);
