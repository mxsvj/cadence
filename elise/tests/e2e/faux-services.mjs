// Chargé dans le serveur Next (NODE_OPTIONS=--import) par lancer.mjs :
// remplace fetch pour imiter Supabase et, si GEMINI_API_KEY=fake, l'API Gemini.
//
// Le faux Supabase repose sur un vrai PostgreSQL en mémoire (PGlite) chargé
// avec supabase/schema.sql : les requêtes de l'application y sont traduites en
// SQL et exécutées avec le rôle et l'identité de la personne connectée, donc
// sous les vraies règles de sécurité (RLS, droits, fonctions). Seul ce que
// l'application utilise est traduit.
//
// Pour les vérifications, l'état est recopié dans le fichier E2E_STATE après
// chaque changement, et un petit serveur (port E2E_CONTROL_PORT) exécute du
// SQL d'administration à la demande de parcours.mjs.
import { PGlite } from "@electric-sql/pglite";
import { randomUUID } from "node:crypto";
import { readFileSync, renameSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import path from "node:path";

const SUPABASE = "http://fake-supabase.test";
const realFetch = globalThis.fetch;
const users = []; // { id, email, password, metadata }
const llmLog = []; // requêtes reçues par le faux Gemini
const webhooks = []; // messages envoyés au faux Discord
let restCalls = 0; // requêtes reçues par le faux Supabase (base de données)

// ─── La base, créée au premier appel (seul le processus qui sert les pages
// en a besoin ; Next en lance d'autres qui chargent aussi ce fichier) ──────
let ready = null;
function database() {
  ready ??= (async () => {
    const db = new PGlite();
    await db.exec(`
      create role anon nologin;
      create role authenticated nologin;
      create role service_role nologin bypassrls;
      create schema auth;
      create table auth.users (id uuid primary key, email text, created_at timestamptz not null default now());
      create function auth.uid() returns uuid language sql stable as $$
        select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
      $$;
      grant usage on schema auth to anon, authenticated, service_role;
      grant usage on schema public to anon, authenticated, service_role;
      alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
      alter default privileges in schema public grant all on functions to anon, authenticated, service_role;
      alter default privileges in schema public grant all on sequences to anon, authenticated, service_role;
    `);
    if (!process.env.FAKE_NO_SCHEMA) {
      await db.exec(readFileSync(path.join(import.meta.dirname, "..", "..", "supabase", "schema.sql"), "utf8"));
    }
    startControlServer();
    return db;
  })();
  return ready;
}

// Une seule requête à la fois : PGlite n'a qu'une connexion.
let queue = Promise.resolve();
function exclusive(fn) {
  const run = queue.then(fn, fn);
  queue = run.catch(() => {});
  return run;
}

const toJson = (value) => JSON.stringify(value, (_, v) => (typeof v === "bigint" ? Number(v) : v));

async function saveState() {
  const db = await database();
  const tables = {};
  for (const t of ["messages", "user_facts", "summaries", "purchases", "admins", "profiles", "contacts",
                   "ai_settings", "scripts", "script_steps", "offers", "creators", "creator_contacts", "team_alerts",
                   "entry_code"]) {
    try {
      tables[t] = (await db.query(`select * from public.${t}`)).rows;
    } catch {
      tables[t] = [];
    }
  }
  // Écrit à côté puis renomme : le lecteur ne voit jamais un fichier à moitié écrit.
  const target = process.env.E2E_STATE;
  writeFileSync(`${target}.tmp`, toJson({ users, tables, llm: llmLog, webhooks, restCalls }));
  renameSync(`${target}.tmp`, target);
}

function startControlServer() {
  const port = process.env.E2E_CONTROL_PORT;
  if (!port) return;
  createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const buffer = Buffer.concat(chunks);
    // Relais : le navigateur ne connaît pas fake-supabase.test ; Playwright lui
    // envoie ses requêtes ici (en-tête x-relay-url), et on les rejoue.
    const relay = req.headers["x-relay-url"];
    if (relay) {
      const headers = Object.fromEntries(
        Object.entries(req.headers).filter(([k]) => !["host", "x-relay-url", "content-length", "connection"].includes(k)),
      );
      const response = await globalThis.fetch(relay, {
        method: req.method,
        headers,
        body: ["GET", "HEAD"].includes(req.method) ? undefined : buffer,
      });
      const body = Buffer.from(await response.arrayBuffer());
      res.writeHead(response.status, {
        "content-type": response.headers.get("content-type") ?? "application/octet-stream",
        "access-control-allow-origin": "*",
      });
      res.end(body);
      return;
    }
    const raw = buffer.toString();
    try {
      const { sql, params = [] } = JSON.parse(raw);
      const rows = await exclusive(async () => (await (await database()).query(sql, params)).rows);
      await exclusive(saveState);
      res.writeHead(200, { "content-type": "application/json" }).end(toJson(rows));
    } catch (err) {
      res.writeHead(400, { "content-type": "application/json" }).end(toJson({ error: String(err.message ?? err) }));
    }
  }).listen(Number(port), "127.0.0.1");
}

// ─── Auth ────────────────────────────────────────────────────────────────
const b64 = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
function jwt(user) {
  const now = Math.floor(Date.now() / 1000);
  const claims = { sub: user.id, email: user.email, role: "authenticated", aud: "authenticated", iat: now, exp: now + 3600, session_id: randomUUID() };
  return `${b64({ alg: "HS256", typ: "JWT" })}.${b64(claims)}.c2lnbmF0dXJl`;
}
function userJson(u) {
  return {
    id: u.id, aud: "authenticated", role: "authenticated", email: u.email,
    email_confirmed_at: new Date().toISOString(), created_at: new Date().toISOString(),
    app_metadata: { provider: "email" }, user_metadata: u.metadata ?? {},
    identities: [{ id: u.id, user_id: u.id, provider: "email", identity_data: { sub: u.id, email: u.email } }],
  };
}
function session(u) {
  return {
    access_token: jwt(u), token_type: "bearer", expires_in: 3600,
    expires_at: Math.floor(Date.now() / 1000) + 3600, refresh_token: `refresh-${u.id}-${randomUUID()}`, user: userJson(u),
  };
}
const json = (status, body, headers = {}) =>
  new Response(body === undefined ? null : toJson(body), {
    status,
    headers: { "content-type": "application/json", "x-supabase-api-version": "2024-01-01", ...headers },
  });
const authError = (status, code, msg) => json(status, { code, error_code: code, msg, message: msg });

const SERVICE = { id: "service" };
/** Les liens de connexion à usage unique (generate_link), jeton → compte. */
const oneTimeTokens = new Map();

/** La clé secrète (côté serveur) : tous les droits, comme le rôle service_role. */
function isService(headers) {
  const key = process.env.SUPABASE_SECRET_KEY;
  return Boolean(key) && headers.get("apikey") === key;
}

function currentUser(headers) {
  if (isService(headers)) return SERVICE;
  const parts = (headers.get("authorization") ?? "").replace(/^Bearer /, "").split(".");
  if (parts.length !== 3) return null;
  try {
    const { sub } = JSON.parse(Buffer.from(parts[1], "base64url").toString());
    return users.find((u) => u.id === sub) ?? null;
  } catch {
    return null;
  }
}

async function handleAuth(url, method, headers, body) {
  const route = url.pathname.replace("/auth/v1", "");
  if (route === "/signup" && method === "POST") {
    if (users.some((u) => u.email === body.email)) return authError(422, "user_already_exists", "User already registered");
    if ((body.password ?? "").length < 6) return authError(422, "weak_password", "Password should be at least 6 characters");
    const u = { id: randomUUID(), email: body.email, password: body.password };
    users.push(u);
    await exclusive(async () => {
      await (await database()).query("insert into auth.users (id, email) values ($1, $2)", [u.id, u.email]);
      await saveState();
    });
    return json(200, session(u));
  }
  if (route === "/token" && url.searchParams.get("grant_type") === "password") {
    const u = users.find((x) => x.email === body.email && x.password === body.password);
    return u ? json(200, session(u)) : authError(400, "invalid_credentials", "Invalid login credentials");
  }
  if (route === "/token" && url.searchParams.get("grant_type") === "refresh_token") {
    const id = String(body.refresh_token ?? "").split("-").slice(1, 6).join("-");
    const u = users.find((x) => x.id === id);
    return u ? json(200, session(u)) : authError(400, "refresh_token_not_found", "Invalid Refresh Token");
  }
  if (route === "/user" && method === "GET") {
    const u = currentUser(headers);
    return u ? json(200, userJson(u)) : authError(403, "bad_jwt", "invalid JWT");
  }
  // Les comptes de test (entrée par le code) : créés par l'API d'administration, sans mot de passe.
  if (route === "/admin/users" && method === "POST") {
    if (!isService(headers)) return authError(401, "no_authorization", "service role required");
    if (users.some((u) => u.email === body.email)) return authError(422, "email_exists", "A user with this email address has already been registered");
    const u = { id: randomUUID(), email: body.email, metadata: body.user_metadata ?? {} };
    users.push(u);
    await exclusive(async () => {
      await (await database()).query("insert into auth.users (id, email) values ($1, $2)", [u.id, u.email]);
      await saveState();
    });
    return json(200, userJson(u));
  }
  // Le lien secret de l'équipe : l'API d'administration (clé secrète) crée un
  // lien de connexion à usage unique, que le serveur échange aussitôt.
  if (route.startsWith("/admin/users/") && method === "GET") {
    if (!isService(headers)) return authError(401, "no_authorization", "service role required");
    const u = users.find((x) => x.id === route.split("/")[3]);
    return u ? json(200, userJson(u)) : authError(404, "user_not_found", "User not found");
  }
  if (route === "/admin/generate_link" && method === "POST") {
    if (!isService(headers)) return authError(401, "no_authorization", "service role required");
    const u = users.find((x) => x.email === body.email);
    if (!u) return authError(404, "user_not_found", "User not found");
    const token = randomUUID();
    oneTimeTokens.set(token, u.id);
    return json(200, {
      action_link: `http://fake-supabase.test/auth/v1/verify?token=${token}&type=${body.type}`,
      email_otp: "123456", hashed_token: token, redirect_to: "", verification_type: body.type, ...userJson(u),
    });
  }
  if (route === "/verify" && method === "POST") {
    const id = oneTimeTokens.get(body.token_hash);
    oneTimeTokens.delete(body.token_hash);
    const u = users.find((x) => x.id === id);
    return u ? json(200, session(u)) : authError(403, "otp_expired", "Email link is invalid or has expired");
  }
  if (route === "/logout") return new Response(null, { status: 204 });
  return authError(404, "not_found", `fake auth: ${method} ${route}`);
}

// ─── PostgREST → SQL ─────────────────────────────────────────────────────
const IDENT = /^[a-z_][a-z0-9_]*$/;
const ident = (name) => {
  if (!IDENT.test(name)) throw Object.assign(new Error(`nom refusé : ${name}`), { code: "PGRST100" });
  return name;
};
const OPS = { eq: "=", neq: "<>", gt: ">", gte: ">=", lt: "<", lte: "<=" };
const RESERVED = new Set(["select", "order", "limit", "offset", "columns", "on_conflict"]);

function condition(key, raw, values) {
  const [op, ...rest] = raw.split(".");
  const operand = rest.join(".");
  if (op === "not") return `not (${condition(key, operand, values)})`;
  if (op === "is") return `${ident(key)} is ${operand === "null" ? "null" : operand === "true" ? "true" : "false"}`;
  if (op === "in") {
    values.push(operand.replace(/^\(|\)$/g, "").split(",").map((v) => v.replace(/^"|"$/g, "")));
    return `${ident(key)} = any($${values.length})`;
  }
  if (OPS[op]) {
    values.push(operand);
    return `${ident(key)} ${OPS[op]} $${values.length}`;
  }
  throw Object.assign(new Error(`opérateur non géré : ${op}`), { code: "PGRST100" });
}
function whereClause(params, values) {
  const parts = [];
  for (const [key, raw] of params) {
    if (RESERVED.has(key)) continue;
    parts.push(condition(key, raw, values));
  }
  return parts.length ? ` where ${parts.join(" and ")}` : "";
}
function orderClause(params) {
  const order = params.get("order");
  if (!order) return "";
  return ` order by ${order
    .split(",")
    .map((o) => {
      const [col, dir] = o.split(".");
      return `${ident(col)} ${dir === "desc" ? "desc" : "asc"}`;
    })
    .join(", ")}`;
}
function columns(params) {
  const select = params.get("select");
  return !select || select === "*" ? "*" : select.split(",").map((c) => ident(c.trim())).join(", ");
}

// Exécute `work(db)` comme le ferait PostgREST pour cette personne.
async function asUser(user, work) {
  return exclusive(async () => {
    const db = await database();
    await db.exec("begin");
    try {
      if (user === SERVICE) {
        await db.exec("set local role service_role");
      } else if (user) {
        await db.query("select set_config('role', 'authenticated', true), set_config('request.jwt.claim.sub', $1, true)", [user.id]);
      } else {
        await db.exec("set local role anon");
      }
      const result = await work(db);
      await db.exec("commit");
      return result;
    } catch (err) {
      await db.exec("rollback");
      throw err;
    }
  });
}

function pgError(err, user) {
  const code = err.code ?? "XX000";
  const message = err.message ?? String(err);
  if (code === "42883") return json(404, { code: "PGRST202", message });
  if (code === "42P01") return json(404, { code: "PGRST205", message });
  if (code === "42501") return json(user ? 403 : 401, { code, message });
  if (code === "23505") return json(409, { code, message });
  return json(400, { code, message });
}

// .single() demande un objet et non une liste (en-tête Accept de PostgREST).
function rowsResponse(status, rows, headers, extra = {}) {
  if ((headers.get("accept") ?? "").includes("vnd.pgrst.object+json")) {
    if (rows.length !== 1) {
      return json(406, { code: "PGRST116", message: `JSON object requested, ${rows.length} rows returned` });
    }
    return json(status, rows[0], extra);
  }
  return json(status, rows, extra);
}

async function handleRest(url, method, headers, body) {
  restCalls++;
  const user = currentUser(headers);
  const route = url.pathname.replace("/rest/v1/", "");
  const prefer = headers.get("prefer") ?? "";
  const params = url.searchParams;
  try {
    if (route.startsWith("rpc/")) {
      const fn = ident(route.slice(4));
      const args = Object.entries(body ?? {});
      const values = args.map(([, v]) => v);
      const call = args.map(([k], i) => `${ident(k)} => $${i + 1}`).join(", ");
      // Une fonction qui renvoie plusieurs lignes (returns table / setof) :
      // PostgREST renvoie un tableau d'objets, comme une table.
      const { rows: kind } = await exclusive(async () =>
        (await database()).query("select bool_or(proretset) as set from pg_proc where proname = $1 and pronamespace = 'public'::regnamespace", [fn]),
      );
      if (kind[0]?.set) {
        const list = await asUser(user, async (db) => (await db.query(`select * from public.${fn}(${call})`, values)).rows);
        await exclusive(saveState);
        return json(200, list);
      }
      // to_jsonb : un objet pour une ligne, la valeur pour un scalaire, null pour void.
      const rows = await asUser(user, async (db) =>
        (await db.query(`select to_jsonb(r) as j from public.${fn}(${call}) as r`, values)).rows,
      );
      await exclusive(saveState);
      const result = rows[0]?.j ?? null;
      // Une fonction « returns void » ne renvoie rien.
      return result === null || result === "" ? new Response(null, { status: 204 }) : json(200, result);
    }

    const table = `public.${ident(route)}`;
    if (method === "GET" || method === "HEAD") {
      const values = [];
      const where = whereClause(params, values);
      const { rows, total } = await asUser(user, async (db) => {
        const limit = params.get("limit") ? ` limit ${Number(params.get("limit"))}` : "";
        const rows = method === "HEAD" ? [] : (await db.query(`select ${columns(params)} from ${table}${where}${orderClause(params)}${limit}`, values)).rows;
        const total = prefer.includes("count=exact")
          ? Number((await db.query(`select count(*) as n from ${table}${where}`, values)).rows[0].n)
          : null;
        return { rows, total };
      });
      const extra = total === null ? {} : { "content-range": `0-${Math.max(total - 1, 0)}/${total}` };
      return method === "HEAD" ? new Response(null, { status: 200, headers: extra }) : rowsResponse(200, rows, headers, extra);
    }

    if (method === "POST") {
      const list = Array.isArray(body) ? body : [body];
      const cols = [...new Set(list.flatMap((r) => Object.keys(r)))].map(ident);
      const values = [];
      const tuples = list.map(
        (r) => `(${cols.map((c) => (c in r ? (values.push(r[c]), `$${values.length}`) : "default")).join(", ")})`,
      );
      let conflict = "";
      if (prefer.includes("resolution=merge-duplicates")) {
        const keys = (params.get("on_conflict") ?? "id").split(",").map(ident);
        const updates = cols.filter((c) => !keys.includes(c)).map((c) => `${c} = excluded.${c}`);
        conflict = ` on conflict (${keys.join(", ")}) do ${updates.length ? `update set ${updates.join(", ")}` : "nothing"}`;
      }
      const rows = await asUser(user, async (db) =>
        (await db.query(`insert into ${table} (${cols.join(", ")}) values ${tuples.join(", ")}${conflict} returning ${columns(params)}`, values)).rows,
      );
      await exclusive(saveState);
      const order = params.get("order");
      if (order?.startsWith("id.")) rows.sort((a, b) => (Number(a.id) - Number(b.id)) * (order.endsWith("desc") ? -1 : 1));
      return prefer.includes("return=representation") ? rowsResponse(201, rows, headers) : new Response(null, { status: 201 });
    }

    if (method === "PATCH") {
      const values = [];
      const set = Object.entries(body).map(([k, v]) => (values.push(v), `${ident(k)} = $${values.length}`));
      const where = whereClause(params, values);
      const rows = await asUser(user, async (db) =>
        (await db.query(`update ${table} set ${set.join(", ")}${where} returning ${columns(params)}`, values)).rows,
      );
      await exclusive(saveState);
      return prefer.includes("return=representation") ? rowsResponse(200, rows, headers) : new Response(null, { status: 204 });
    }
    if (method === "DELETE") {
      const values = [];
      const where = whereClause(params, values);
      await asUser(user, (db) => db.query(`delete from ${table}${where}`, values));
      await exclusive(saveState);
      return new Response(null, { status: 204 });
    }
    return json(405, { message: `fake postgrest : ${method} non géré` });
  } catch (err) {
    return pgError(err, user);
  }
}

// ─── Stockage (fichiers en mémoire, liens signés) ─────────────────────────
const files = new Map(); // "bucket/chemin" → { body, type }
const tokens = new Map(); // jeton → "bucket/chemin"

async function handleStorage(url, method, headers, rawBody) {
  const route = url.pathname.replace("/storage/v1", "");
  const token = url.searchParams.get("token");
  let m;
  if ((m = route.match(/^\/object\/upload\/sign\/(.+)$/))) {
    const key = decodeURIComponent(m[1]);
    if (method === "POST") {
      if (!isService(headers)) return json(403, { error: "service_role requis" });
      const t = randomUUID();
      tokens.set(t, key);
      return json(200, { url: `/object/upload/sign/${key}?token=${t}` });
    }
    if (method === "PUT") {
      if (tokens.get(token) !== key) return json(400, { error: "jeton invalide" });
      files.set(key, { body: rawBody, type: headers.get("content-type") ?? "application/octet-stream" });
      return json(200, { Key: key });
    }
  }
  if ((m = route.match(/^\/object\/sign\/(.+)$/))) {
    const key = decodeURIComponent(m[1]);
    if (method === "POST") {
      if (!isService(headers)) return json(403, { error: "service_role requis" });
      if (!files.has(key)) return json(404, { error: "introuvable" });
      const t = randomUUID();
      tokens.set(t, key);
      return json(200, { signedURL: `/object/sign/${key}?token=${t}` });
    }
    if (method === "GET") {
      const file = files.get(key);
      if (tokens.get(token) !== key || !file) return json(400, { error: "jeton invalide" });
      return new Response(file.body, { status: 200, headers: { "content-type": file.type } });
    }
  }
  if ((m = route.match(/^\/object\/([^/]+)$/)) && method === "DELETE") {
    if (!isService(headers)) return json(403, { error: "service_role requis" });
    const { prefixes = [] } = JSON.parse(rawBody.toString() || "{}");
    for (const p of prefixes) files.delete(`${m[1]}/${p}`);
    return json(200, []);
  }
  return json(404, { error: `fake storage : ${method} ${route}` });
}

// ─── Faux Gemini ─────────────────────────────────────────────────────────
function gemini(body, model) {
  const system = body.systemInstruction.parts[0].text;
  const contents = body.contents;
  const last = contents[contents.length - 1].parts[0].text;
  llmLog.push({ model, system, contents, json: body.generationConfig?.responseMimeType === "application/json" });
  const reply = (text) => json(200, { candidates: [{ content: { parts: [{ text }] }, finishReason: "STOP" }] });

  if (system.includes("fiche mémoire")) {
    const faits = [];
    const name = last.match(/moi c'est (\p{L}+)/u);
    if (name) faits.push(`Se prénomme ${name[1]}.`, "Préfère le tutoiement.");
    if (/antid/.test(last)) faits.push("Prend des antidépresseurs.");
    if (/chat/.test(last)) faits.push("A un chat, Filou.", "a un chat, filou");
    return reply(JSON.stringify({ faits }));
  }
  // Prendre des nouvelles : avec une balise, pour vérifier qu'elle est retirée.
  if (system.includes("Ta tâche maintenant : prendre de ses nouvelles")) {
    return reply("Coucou ! **Comment** s'est passée ta semaine à Lyon ?\n[[PROPOSER]]");
  }
  if (system.includes("## Ta tâche")) return reply("Un petit carnet rien que pour toi, si le cœur t'en dit.");
  if (system.includes("carnet de mémoire")) {
    const n = (last.match(/La personne :/g) ?? []).length;
    return reply(`Résumé de test : ${n} messages de la personne résumés.`);
  }
  const userText = contents.filter((c) => c.role === "user").at(-1).parts[0].text;
  if (userText.includes("QUOTA")) return json(429, { error: { code: 429, message: "Resource exhausted" } });
  // Le modèle principal surchargé : le modèle de secours doit prendre le relais.
  if (userText.includes("SURCHARGE") && model === "gemini-flash-latest") {
    return json(503, { error: { code: 503, message: "The model is overloaded. Please try again later." } });
  }
  // L'IA juge qu'un humain doit lire la conversation.
  if (userText.includes("ALERTE-IA")) return reply("Je préviens l'équipe, elle te répondra ici.\n[[EQUIPE]]");
  if (userText.includes("PROPOSE-MOI") && system.includes("termine ta réponse par une ligne contenant uniquement")) {
    return system.includes("[[PROPOSER prix=NN]]")
      ? reply("Je t'ai préparé quelque chose.\n[[PROPOSER prix=9]]")
      : reply("Un petit cadeau pour toi.\n[[PROPOSER]]");
  }
  // Les réponses numérotées : une par message (les essais refusés et le secours ne comptent pas).
  const n = llmLog.filter(
    (r) =>
      !r.system.includes("fiche mémoire") &&
      !r.system.includes("carnet de mémoire") &&
      !r.system.includes("## Ta tâche") &&
      !/QUOTA|SURCHARGE/.test(r.contents.filter((c) => c.role === "user").at(-1).parts[0].text),
  ).length;
  return reply(`C'est noté. **Merci** de me le dire. (réponse de test n° ${n})`);
}

globalThis.fetch = async function fakeFetch(input, init = {}) {
  const url = new URL(typeof input === "string" ? input : (input.url ?? String(input)));
  const method = (init.method ?? input.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers ?? input.headers);
  const raw = init.body ?? null;
  if (url.origin === SUPABASE && url.pathname.startsWith("/storage/v1")) {
    const bytes = raw ? Buffer.from(await new Response(raw).arrayBuffer()) : Buffer.alloc(0);
    return handleStorage(url, method, headers, bytes);
  }
  const text = raw ? (typeof raw === "string" ? raw : await new Response(raw).text()) : "";
  const body = text ? JSON.parse(text) : {};

  if (url.origin === SUPABASE) {
    return url.pathname.startsWith("/auth/v1") ? handleAuth(url, method, headers, body) : handleRest(url, method, headers, body);
  }
  if (url.hostname === "discord.com" && url.pathname.startsWith("/api/webhooks/")) {
    webhooks.push(body);
    await exclusive(saveState);
    return new Response(null, { status: 204 });
  }
  if (url.hostname === "generativelanguage.googleapis.com" && process.env.GEMINI_API_KEY === "fake") {
    const res = gemini(body, url.pathname.match(/models\/([^:]+):/)?.[1] ?? "");
    await exclusive(saveState);
    return res;
  }
  return realFetch(input, init);
};
