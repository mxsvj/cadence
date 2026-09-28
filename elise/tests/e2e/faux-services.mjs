// Chargé dans le serveur Next (NODE_OPTIONS=--import) par lancer.mjs :
// remplace fetch pour imiter Supabase (Auth + PostgREST, avec le cloisonnement
// par utilisateur) et, si GEMINI_API_KEY=fake, l'API Gemini. Seul ce que
// l'application utilise est imité. L'état est recopié dans le fichier
// E2E_STATE après chaque changement, pour que parcours.mjs le vérifie.
import { writeFileSync } from "node:fs";
import { randomUUID } from "node:crypto";

const SUPABASE = "http://fake-supabase.test";
const STATE_FILE = process.env.E2E_STATE;
const realFetch = globalThis.fetch;

const state = {
  users: [], // { id, email, password }
  tables: { messages: [], user_facts: [], summaries: [] },
  seq: { messages: 0, user_facts: 0 },
  llm: [], // requêtes reçues par le faux Gemini
};
const save = () => writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
save();

const b64 = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
function jwt(user) {
  const now = Math.floor(Date.now() / 1000);
  return `${b64({ alg: "HS256", typ: "JWT" })}.${b64({ sub: user.id, email: user.email, role: "authenticated", aud: "authenticated", iat: now, exp: now + 3600, session_id: randomUUID() })}.c2lnbmF0dXJl`;
}
function userJson(u) {
  return {
    id: u.id, aud: "authenticated", role: "authenticated", email: u.email,
    email_confirmed_at: new Date().toISOString(), created_at: new Date().toISOString(),
    app_metadata: { provider: "email" }, user_metadata: {},
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
  new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "x-supabase-api-version": "2024-01-01", ...headers },
  });
const authError = (status, code, msg) => json(status, { code, error_code: code, msg, message: msg });

function currentUser(headers) {
  const token = (headers.get("authorization") ?? "").replace(/^Bearer /, "");
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const { sub } = JSON.parse(Buffer.from(parts[1], "base64url").toString());
    return state.users.find((u) => u.id === sub) ?? null;
  } catch {
    return null;
  }
}

async function handleAuth(url, method, headers, body) {
  const path = url.pathname.replace("/auth/v1", "");
  if (path === "/signup" && method === "POST") {
    if (state.users.some((u) => u.email === body.email)) return authError(422, "user_already_exists", "User already registered");
    if ((body.password ?? "").length < 6) return authError(422, "weak_password", "Password should be at least 6 characters");
    const u = { id: randomUUID(), email: body.email, password: body.password };
    state.users.push(u);
    save();
    return json(200, session(u));
  }
  if (path === "/token" && url.searchParams.get("grant_type") === "password") {
    const u = state.users.find((x) => x.email === body.email && x.password === body.password);
    return u ? json(200, session(u)) : authError(400, "invalid_credentials", "Invalid login credentials");
  }
  if (path === "/token" && url.searchParams.get("grant_type") === "refresh_token") {
    const id = String(body.refresh_token ?? "").split("-").slice(1, 6).join("-");
    const u = state.users.find((x) => x.id === id);
    return u ? json(200, session(u)) : authError(400, "refresh_token_not_found", "Invalid Refresh Token");
  }
  if (path === "/user" && method === "GET") {
    const u = currentUser(headers);
    return u ? json(200, userJson(u)) : authError(403, "bad_jwt", "invalid JWT");
  }
  if (path === "/logout") return new Response(null, { status: 204 });
  return authError(404, "not_found", `fake auth: ${method} ${path}`);
}

// ─── PostgREST, strictement ce qu'utilise l'application ────────────────────
function applyFilters(rows, params) {
  let out = rows;
  for (const [key, value] of params) {
    if (["select", "order", "limit", "offset", "columns", "on_conflict"].includes(key)) continue;
    const [op, ...rest] = value.split(".");
    const operand = rest.join(".");
    out = out.filter((r) => {
      const v = r[key];
      if (op === "eq") return String(v) === operand;
      if (op === "gt") return Number(v) > Number(operand);
      if (op === "lt") return Number(v) < Number(operand);
      throw new Error(`fake postgrest: opérateur ${op} non géré`);
    });
  }
  const order = params.get("order");
  if (order) {
    const [col, dir] = order.split(".");
    out = [...out].sort((a, b) => (a[col] < b[col] ? -1 : a[col] > b[col] ? 1 : 0) * (dir === "desc" ? -1 : 1));
  }
  const limit = params.get("limit");
  if (limit) out = out.slice(0, Number(limit));
  return out;
}
function pick(rows, select) {
  if (!select || select === "*") return rows;
  const cols = select.split(",").map((c) => c.trim());
  return rows.map((r) => Object.fromEntries(cols.map((c) => [c, r[c]])));
}

async function handleRest(url, method, headers, body) {
  if (process.env.FAKE_NO_TABLES) {
    return json(404, { code: "PGRST205", message: "Could not find the table 'public.messages' in the schema cache" });
  }
  const user = currentUser(headers);
  const path = url.pathname.replace("/rest/v1/", "");
  const prefer = headers.get("prefer") ?? "";

  if (path === "rpc/effacer_mes_donnees") {
    if (!user) return json(401, { code: "42501", message: "permission denied" });
    for (const t of Object.keys(state.tables)) state.tables[t] = state.tables[t].filter((r) => r.user_id !== user.id);
    save();
    return new Response(null, { status: 204 });
  }

  const table = state.tables[path];
  if (!table) return json(404, { code: "PGRST205", message: `table ${path} inconnue` });
  if (!user) return json(401, { code: "42501", message: "permission denied for table" });
  const own = table.filter((r) => r.user_id === user.id); // Row Level Security

  if (method === "GET" || method === "HEAD") {
    const rows = applyFilters(own, url.searchParams);
    const extra = prefer.includes("count=exact") ? { "content-range": `0-${Math.max(rows.length - 1, 0)}/${rows.length}` } : {};
    if (method === "HEAD") return new Response(null, { status: 200, headers: extra });
    return json(200, pick(rows, url.searchParams.get("select")), extra);
  }

  if (method === "POST") {
    const inserted = [];
    for (const input of Array.isArray(body) ? body : [body]) {
      const row = { ...input, user_id: input.user_id ?? user.id };
      if (row.user_id !== user.id) return json(403, { code: "42501", message: "new row violates row-level security policy" });
      if (path === "user_facts" && own.some((r) => r.fact.toLowerCase() === row.fact.toLowerCase())) {
        return json(409, { code: "23505", message: "duplicate key value violates unique constraint" });
      }
      if (path === "summaries" && own.length) return json(409, { code: "23505", message: "duplicate key" });
      if (path !== "summaries") row.id = ++state.seq[path];
      row.created_at ??= new Date().toISOString();
      if (path === "summaries") row.updated_at ??= new Date().toISOString();
      inserted.push(row);
    }
    table.push(...inserted);
    save();
    if (prefer.includes("return=representation")) {
      return json(201, pick(applyFilters(inserted, new URLSearchParams([["order", url.searchParams.get("order") ?? ""]].filter(([, v]) => v))), url.searchParams.get("select")));
    }
    return new Response(null, { status: 201 });
  }

  if (method === "PATCH") {
    const targets = applyFilters(own, url.searchParams);
    for (const r of targets) Object.assign(r, body, { user_id: user.id });
    save();
    return new Response(null, { status: 204 });
  }
  return json(405, { message: `fake postgrest: ${method} non géré` });
}

// ─── Faux Gemini ───────────────────────────────────────────────────────────
function gemini(body) {
  const system = body.systemInstruction.parts[0].text;
  const contents = body.contents;
  const last = contents[contents.length - 1].parts[0].text;
  state.llm.push({ system, contents, json: body.generationConfig?.responseMimeType === "application/json" });
  save();
  const reply = (text) => json(200, { candidates: [{ content: { parts: [{ text }] }, finishReason: "STOP" }] });

  if (system.includes("fiche mémoire")) {
    const faits = [];
    const name = last.match(/moi c'est (\p{L}+)/u);
    if (name) faits.push(`Se prénomme ${name[1]}.`, "Préfère le tutoiement.");
    if (/antid/.test(last)) faits.push("Prend des antidépresseurs.");
    if (/chat/.test(last)) faits.push("A un chat, Filou.", "a un chat, filou");
    return reply(JSON.stringify({ faits }));
  }
  if (system.includes("carnet de mémoire")) {
    const n = (last.match(/La personne :/g) ?? []).length;
    return reply(`Résumé de test : ${n} messages de la personne résumés.`);
  }
  const userText = contents.filter((c) => c.role === "user").at(-1).parts[0].text;
  if (userText.includes("QUOTA")) return json(429, { error: { code: 429, message: "Resource exhausted" } });
  const n = state.llm.filter((r) => !r.system.includes("fiche mémoire") && !r.system.includes("carnet")).length;
  return reply(`C'est noté. **Merci** de me le dire. (réponse de test n° ${n})`);
}

globalThis.fetch = async function fakeFetch(input, init = {}) {
  const url = new URL(typeof input === "string" ? input : input.url ?? String(input));
  const method = (init.method ?? input.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers ?? input.headers);
  const raw = init.body ?? null;
  const body = raw ? JSON.parse(typeof raw === "string" ? raw : await new Response(raw).text()) : {};

  if (url.origin === SUPABASE) {
    return url.pathname.startsWith("/auth/v1") ? handleAuth(url, method, headers, body) : handleRest(url, method, headers, body);
  }
  if (url.hostname === "generativelanguage.googleapis.com" && process.env.GEMINI_API_KEY === "fake") {
    return gemini(body);
  }
  return realFetch(input, init);
};
