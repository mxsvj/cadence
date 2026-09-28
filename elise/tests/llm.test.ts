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
