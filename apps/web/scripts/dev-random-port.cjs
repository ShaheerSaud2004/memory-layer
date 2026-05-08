/* Spawns Next.js on a free loopback TCP port (avoids EADDRINUSE). */
const { createServer } = require("node:net");
const { spawn } = require("node:child_process");
const path = require("node:path");
const { createRequire } = require("node:module");

const root = path.join(__dirname, "..");
const requireFromWeb = createRequire(path.join(root, "package.json"));

function freePort() {
  return new Promise((resolve, reject) => {
    const s = createServer();
    s.unref();
    s.on("error", reject);
    s.listen(0, "127.0.0.1", () => {
      const addr = s.address();
      const p = typeof addr === "object" && addr ? addr.port : null;
      s.close((err) => (err ? reject(err) : resolve(p)));
    });
  });
}

function resolveNextBin() {
  try {
    return requireFromWeb.resolve("next/dist/bin/next");
  } catch {
    return null;
  }
}

async function main() {
  const port = await freePort();
  if (!port) {
    throw new Error("Could not allocate a free port");
  }
  console.error(`\n  ▲ Next.js  http://127.0.0.1:${port}\n`);

  const nextBin = resolveNextBin();
  if (!nextBin) {
    console.error("Run `npm install` in apps/web first.");
    process.exit(1);
  }

  const child = spawn(process.execPath, [nextBin, "dev", "-H", "127.0.0.1", "-p", String(port)], {
    cwd: root,
    stdio: "inherit",
    env: process.env,
  });

  child.on("exit", (code) => process.exit(code ?? 0));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
