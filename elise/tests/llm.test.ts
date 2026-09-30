// Vérifie ce que lib/llm.ts envoie à chaque fournisseur, sans appel réel :
// on remplace fetch par une imitation qui enregistre la requête.
import assert from "node:assert/strict";
import { afterEach, beforeEach, describe, it } from "node:test";
import { LlmError, generate } from "../lib/llm";

type Captured = { url: string; headers: Record<string, string>; body: Record<string, unknown> };

const realFetch = globalThis.fetch;
const savedEnv = { ...process.env };
let captured: Captured[] = [];

function answer(status: number, json: unknown) {
  globalThis.fetch = (async (url: string, init: RequestInit) => {
    captured.push({
      url: String(url),
      headers: init.headers as Record<string, string>,
      body: JSON.parse(String(init.body)),
    });
    return new Response(JSON.stringify(json), { status });
  }) as typeof fetch;
}

beforeEach(() => {
  captured = [];
  process.env = { ...savedEnv, GEMINI_API_KEY: "cle-gemini", ANTHROPIC_API_KEY: "cle-claude" };
  delete process.env.LLM_PROVIDER;
  delete process.env.GEMINI_MODEL;
  delete process.env.GEMINI_FALLBACK_MODEL;
  delete process.env.CLAUDE_MODEL;
});
afterEach(() => {
  globalThis.fetch = realFetch;
  process.env = savedEnv;
});

const conversation = {
  system: "Tu es Élise.",
  messages: [
    { role: "assistant" as const, content: "Bonjour, je suis Élise." },
    { role: "user" as const, content: "Salut !" },
    { role: "user" as const, content: "Tu es là ?" },
  ],
  maxTokens: 300,
};

describe("Gemini (par défaut)", () => {
  it("envoie la persona en instruction système et une conversation qui alterne", async () => {
    answer(200, { candidates: [{ content: { parts: [{ text: "réflexion", thought: true }, { text: "Oui, je suis là." }] } }] });
    const reply = await generate(conversation);

    assert.equal(reply, "Oui, je suis là.");
    const [req] = captured;
    assert.equal(req.url, "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent");
    assert.equal(req.headers["x-goog-api-key"], "cle-gemini");
    assert.deepEqual(req.body.systemInstruction, { parts: [{ text: "Tu es Élise." }] });
    assert.deepEqual(
      (req.body.contents as { role: string; parts: { text: string }[] }[]).map((c) => [c.role, c.parts[0].text]),
      [
        ["user", "(La personne ouvre la conversation.)"],
        ["model", "Bonjour, je suis Élise."],
        ["user", "Salut !\n\nTu es là ?"],
      ],
    );
  });

  it("respecte GEMINI_MODEL et le mode JSON", async () => {
    process.env.GEMINI_MODEL = "gemini-autre-flash";
    answer(200, { candidates: [{ content: { parts: [{ text: '{"faits": []}' }] } }] });
    await generate({ ...conversation, json: true });
    assert.match(captured[0].url, /models\/gemini-autre-flash:generateContent$/);
    assert.equal((captured[0].body.generationConfig as Record<string, unknown>).responseMimeType, "application/json");
  });

  it("signale le quota atteint", async () => {
    answer(429, { error: { message: "quota" } });
    await assert.rejects(generate(conversation), (err: unknown) => err instanceof LlmError && err.kind === "rate_limited");
  });

  it("signale une réponse bloquée", async () => {
    answer(200, { promptFeedback: { blockReason: "SAFETY" } });
    await assert.rejects(generate(conversation), (err: unknown) => err instanceof LlmError && err.kind === "blocked");
  });

  it("réessaie une fois quand le service est surchargé", async () => {
    let calls = 0;
    globalThis.fetch = (async () => {
      calls += 1;
      return calls === 1
        ? new Response("{}", { status: 503 })
        : new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: "Me revoilà." }] } }] }), { status: 200 });
    }) as typeof fetch;
    assert.equal(await generate(conversation), "Me revoilà.");
    assert.equal(calls, 2);
  });
});

describe("Gemini : le modèle de secours", () => {
  const ok = (text: string) => new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text }] } }] }), { status: 200 });
  /** Répond selon le modèle demandé ; garde la liste des modèles appelés. */
  function byModel(responses: Record<string, (() => Response) | "réseau">) {
    const models: string[] = [];
    globalThis.fetch = (async (url: string) => {
      const model = String(url).match(/models\/([^:]+):/)?.[1] ?? "";
      models.push(model);
      const r = responses[model];
      if (r === "réseau") throw new TypeError("fetch failed");
      return r ? r() : new Response("{}", { status: 500 });
    }) as typeof fetch;
    return models;
  }

  it("le principal surchargé deux fois : le secours répond, et on sait lequel", async () => {
    const models = byModel({ "gemini-flash-latest": () => new Response("{}", { status: 503 }), "gemini-flash-lite-latest": () => ok("Coucou !") });
    let served = "";
    assert.equal(await generate({ ...conversation, onModel: (m) => (served = m) }), "Coucou !");
    assert.deepEqual(models, ["gemini-flash-latest", "gemini-flash-latest", "gemini-flash-lite-latest"]);
    assert.equal(served, "gemini-flash-lite-latest");
  });

  it("un modèle retiré (404), un réseau coupé ou un quota de la minute : le secours prend le relais", async () => {
    for (const trouble of [() => new Response("{}", { status: 404 }), "réseau" as const, () => new Response("{}", { status: 429 })]) {
      const models = byModel({ "gemini-flash-latest": trouble, "gemini-flash-lite-latest": () => ok("Présente !") });
      assert.equal(await generate(conversation), "Présente !");
      assert.deepEqual(models, ["gemini-flash-latest", "gemini-flash-lite-latest"]);
    }
  });

  it("les deux à court de quota : « réessayez dans une minute »", async () => {
    const models = byModel({ "gemini-flash-latest": () => new Response("{}", { status: 429 }), "gemini-flash-lite-latest": () => new Response("{}", { status: 429 }) });
    await assert.rejects(generate(conversation), (err: unknown) => err instanceof LlmError && err.kind === "rate_limited");
    assert.equal(models.length, 2);
  });

  it("pas de secours quand un autre modèle n'y changerait rien : clé refusée, contenu bloqué", async () => {
    let models = byModel({ "gemini-flash-latest": () => new Response('{"error":"API key not valid"}', { status: 400 }) });
    await assert.rejects(generate(conversation), (err: unknown) => err instanceof LlmError && err.kind === "failed" && err.status === 400);
    assert.deepEqual(models, ["gemini-flash-latest"]);
    models = byModel({ "gemini-flash-latest": () => new Response(JSON.stringify({ promptFeedback: { blockReason: "SAFETY" } }), { status: 200 }) });
    await assert.rejects(generate(conversation), (err: unknown) => err instanceof LlmError && err.kind === "blocked");
    assert.deepEqual(models, ["gemini-flash-latest"]);
  });

  it("GEMINI_FALLBACK_MODEL choisit le secours ; « aucun » le désactive", async () => {
    process.env.GEMINI_FALLBACK_MODEL = "gemini-autre";
    let models = byModel({ "gemini-flash-latest": () => new Response("{}", { status: 404 }), "gemini-autre": () => ok("Oui ?") });
    assert.equal(await generate(conversation), "Oui ?");
    assert.deepEqual(models, ["gemini-flash-latest", "gemini-autre"]);
    process.env.GEMINI_FALLBACK_MODEL = "aucun";
    models = byModel({ "gemini-flash-latest": () => new Response("{}", { status: 404 }) });
    await assert.rejects(generate(conversation), (err: unknown) => err instanceof LlmError && err.status === 404);
    assert.deepEqual(models, ["gemini-flash-latest"]);
  });
});

describe("Claude : une seule variable à changer", () => {
  it("LLM_PROVIDER=claude envoie la même conversation à l'API Claude (Haiku 4.5)", async () => {
    process.env.LLM_PROVIDER = "claude";
    answer(200, { content: [{ type: "text", text: "Oui, je suis là." }], stop_reason: "end_turn" });
    const reply = await generate(conversation);

    assert.equal(reply, "Oui, je suis là.");
    const [req] = captured;
    assert.equal(req.url, "https://api.anthropic.com/v1/messages");
    assert.equal(req.headers["x-api-key"], "cle-claude");
    assert.equal(req.headers["anthropic-version"], "2023-06-01");
    assert.equal(req.body.model, "claude-haiku-4-5-20251001");
    assert.equal(req.body.max_tokens, 300);
    assert.equal(req.body.system, "Tu es Élise.");
    assert.deepEqual(req.body.messages, [
      { role: "user", content: "(La personne ouvre la conversation.)" },
      { role: "assistant", content: "Bonjour, je suis Élise." },
      { role: "user", content: "Salut !\n\nTu es là ?" },
    ]);
  });

  it("explique la clé manquante", async () => {
    process.env.LLM_PROVIDER = "claude";
    delete process.env.ANTHROPIC_API_KEY;
    await assert.rejects(generate(conversation), /ANTHROPIC_API_KEY est absente/);
  });
});
