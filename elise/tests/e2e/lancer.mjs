// Essai de bout en bout, en une commande : npm run test:e2e
//   1. construit le site en le branchant sur un faux Supabase ;
//   2. le démarre avec faux-services.mjs (faux Supabase + faux Gemini) ;
//   3. joue parcours.mjs dans Chromium, puis arrête tout.
// Aucune clé ni aucun compte n'est nécessaire. Les captures d'écran sont
// rangées dans le dossier indiqué à la fin.
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const here = import.meta.dirname;
const root = path.join(here, "..", "..");
const work = mkdtempSync(path.join(tmpdir(), "elise-e2e-"));
const port = process.env.E2E_PORT ?? "3100";
const env = {
  ...process.env,
  NEXT_PUBLIC_SUPABASE_URL: "http://fake-supabase.test",
  NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "sb_publishable_fake",
  LLM_PROVIDER: "gemini",
  GEMINI_API_KEY: "fake",
  E2E_STATE: path.join(work, "etat.json"),
  E2E_SHOTS: path.join(work, "captures"),
  E2E_BASE: `http://localhost:${port}`,
};

const build = spawnSync("npx", ["next", "build"], { cwd: root, env, stdio: "inherit" });
if (build.status !== 0) process.exit(build.status ?? 1);

const server = spawn("npx", ["next", "start", "-p", port], {
  cwd: root,
  env: { ...env, NODE_OPTIONS: `--import ${path.join(here, "faux-services.mjs")}` },
  stdio: ["ignore", "inherit", "inherit"],
  detached: true, // pour pouvoir arrêter aussi le processus enfant de Next
});
const stop = () => {
  try {
    process.kill(-server.pid, "SIGTERM");
  } catch {}
};
process.on("exit", stop);

let ready = false;
for (let i = 0; i < 60 && !ready; i++) {
  await new Promise((r) => setTimeout(r, 500));
  ready = await fetch(`${env.E2E_BASE}/connexion`).then(() => true, () => false);
}
if (!ready) {
  console.error("Le serveur n'a pas démarré.");
  process.exit(1);
}

const run = spawnSync("node", [path.join(here, "parcours.mjs")], { env, stdio: "inherit" });
console.log(`\nCaptures d'écran : ${env.E2E_SHOTS}`);
process.exit(run.status ?? 1);
