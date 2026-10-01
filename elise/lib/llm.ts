import "server-only";

// Le seul fichier qui parle à un modèle de langage. Tout le reste de
// l'application appelle `generate()` et ignore quel fournisseur répond.
//
// Changer de fournisseur = changer la variable d'environnement LLM_PROVIDER :
//   LLM_PROVIDER=gemini  → API Gemini (offre gratuite, développement uniquement :
//                          Google peut réutiliser les données envoyées)
//   LLM_PROVIDER=claude  → API Claude (Haiku 4.5)
// La clé du fournisseur choisi doit être présente (GEMINI_API_KEY ou
// ANTHROPIC_API_KEY). Le modèle se règle avec GEMINI_MODEL ou CLAUDE_MODEL.

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type GenerateOptions = {
  /** L'instruction système : la persona, la fiche, le résumé… */
  system: string;
  /** La conversation, du plus ancien au plus récent. */
  messages: ChatMessage[];
  /** Longueur maximale de la réponse, en jetons (environ ¾ de mot chacun). */
  maxTokens?: number;
  /** 0 = toujours la même réponse, 1 = plus de variété. */
  temperature?: number;
  /** Demande une réponse en JSON seul, sans texte autour. */
  json?: boolean;
  /** Appelé avec le modèle qui a vraiment répondu (le principal ou celui de secours). */
  onModel?: (model: string) => void;
  /** Gemini : un autre modèle que le principal (par exemple `lightModel()`). Ignoré pour Claude. */
  model?: string;
};

export class LlmError extends Error {
  constructor(
    message: string,
    /** `rate_limited` : quota gratuit atteint pour la minute ou la journée. */
    readonly kind: "rate_limited" | "blocked" | "config" | "failed",
    /** Le code HTTP du fournisseur, s'il a répondu. */
    readonly status?: number,
  ) {
    super(message);
    this.name = "LlmError";
  }
}

const DEFAULTS = {
  gemini: "gemini-flash-latest",
  claude: "claude-haiku-4-5-20251001",
};

/**
 * Le modèle de secours de Gemini, quand le principal ne répond pas
 * (surchargé, quota de la minute atteint, retiré par Google) : un autre
 * modèle Flash, dont le quota gratuit est séparé. GEMINI_FALLBACK_MODEL le
 * change ; « aucun » le désactive.
 */
const GEMINI_FALLBACK = "gemini-flash-lite-latest";

/** Tout doit tenir avant que Vercel coupe la fonction (60 s), secours compris. */
const BUDGET_MS = 50_000;
/** Le temps laissé au modèle principal avant de passer au secours. */
const PRIMARY_MS = 30_000;

/**
 * La créativité des réponses : la plus haute qui reste fiable. C'est aussi
 * la valeur que Google recommande pour ses modèles récents (au-delà, l'IA
 * devient incohérente ; en dessous, plus plate et répétitive).
 */
export const CHAT_TEMPERATURE = 1;

/** Le fournisseur et le modèle en service, pour l'onglet Paramètres. */
export function currentModel(): { provider: string; model: string } {
  const provider = (process.env.LLM_PROVIDER ?? "gemini").trim().toLowerCase();
  if (provider === "claude") return { provider, model: process.env.CLAUDE_MODEL?.trim() || DEFAULTS.claude };
  return { provider, model: process.env.GEMINI_MODEL?.trim() || DEFAULTS.gemini };
}

/** Le petit modèle Gemini des tâches de fond (profil de discussion) : son quota gratuit est séparé. */
export function lightModel(): string {
  return process.env.GEMINI_LIGHT_MODEL?.trim() || GEMINI_FALLBACK;
}

/** Le modèle de secours de Gemini, ou null s'il est désactivé. */
export function fallbackModel(): string | null {
  const model = process.env.GEMINI_FALLBACK_MODEL?.trim() || GEMINI_FALLBACK;
  return model.toLowerCase() === "aucun" ? null : model;
}

export async function generate(options: GenerateOptions): Promise<string> {
  const provider = (process.env.LLM_PROVIDER ?? "gemini").trim().toLowerCase();
  const messages = normalize(options.messages);

  if (provider === "gemini") return callGemini({ ...options, messages });
  if (provider === "claude") return callClaude({ ...options, messages });
  throw new LlmError(
    `LLM_PROVIDER vaut « ${provider} » : les valeurs possibles sont gemini ou claude.`,
    "config",
  );
}

// Les deux API veulent une conversation qui commence par l'utilisateur et
// alterne les rôles. Or celle d'Élise commence par son propre message
// d'accueil : on la fait précéder d'un repère, et on fusionne les messages
// consécutifs d'un même auteur.
function normalize(messages: ChatMessage[]): ChatMessage[] {
  const out: ChatMessage[] = [];
  for (const m of messages) {
    const content = m.content.trim();
    if (!content) continue;
    const last = out[out.length - 1];
    if (last && last.role === m.role) last.content += `\n\n${content}`;
    else out.push({ role: m.role, content });
  }
  if (out.length === 0 || out[0].role !== "user") {
    out.unshift({ role: "user", content: "(La personne ouvre la conversation.)" });
  }
  return out;
}

function requireEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) throw new LlmError(`La variable d'environnement ${name} est absente.`, "config");
  return value;
}

/** `deadline` : l'heure (Date.now()) à laquelle on abandonne. */
async function post(url: string, headers: Record<string, string>, body: unknown, deadline: number, retry = true) {
  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json", ...headers },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(Math.max(1000, deadline - Date.now())),
      cache: "no-store",
    });
  } catch (err) {
    const late = (err as Error).name === "TimeoutError";
    throw new LlmError(late ? "Le modèle a mis trop longtemps à répondre." : `Le modèle n'a pas répondu : ${(err as Error).message}`, "failed");
  }
  const text = await res.text();
  if (res.status === 429) throw new LlmError(`Quota du modèle atteint : ${text.slice(0, 300)}`, "rate_limited", 429);
  // Surcharge passagère du côté du fournisseur : une seconde chance, s'il reste le temps.
  if (res.status >= 500 && retry && deadline - Date.now() > 8000) {
    await new Promise((r) => setTimeout(r, 1500));
    return post(url, headers, body, deadline, false);
  }
  if (!res.ok) {
    throw new LlmError(`Le modèle a répondu ${res.status} : ${text.slice(0, 500)}`, "failed", res.status);
  }
  try {
    return JSON.parse(text);
  } catch {
    throw new LlmError(`Réponse illisible du modèle : ${text.slice(0, 200)}`, "failed");
  }
}

type Ready = GenerateOptions & { messages: ChatMessage[] };

// ─── Gemini ────────────────────────────────────────────────────────────────

type GeminiResponse = {
  candidates?: {
    content?: { parts?: { text?: string; thought?: boolean }[] };
    finishReason?: string;
  }[];
  promptFeedback?: { blockReason?: string };
};

async function callGemini(o: Ready): Promise<string> {
  const key = requireEnv("GEMINI_API_KEY");
  const primary = o.model?.trim() || process.env.GEMINI_MODEL?.trim() || DEFAULTS.gemini;
  const backup = fallbackModel();
  const start = Date.now();
  try {
    const text = await askGemini(key, primary, o, backup ? start + PRIMARY_MS : start + BUDGET_MS);
    o.onModel?.(primary);
    return text;
  } catch (err) {
    if (!backup || backup === primary || !worthFallback(err)) throw err;
    console.error(`Gemini ${primary} : ${(err as Error).message} Essai avec ${backup}.`);
    const text = await askGemini(key, backup, o, start + BUDGET_MS);
    o.onModel?.(backup);
    return text;
  }
}

/**
 * Un autre modèle a sa chance quand le principal est surchargé, lent,
 * introuvable ou à court de quota ; pas quand la clé manque ou que le
 * contenu est refusé (un autre modèle n'y changerait rien).
 */
function worthFallback(err: unknown): boolean {
  if (!(err instanceof LlmError)) return false;
  if (err.kind === "rate_limited") return true;
  if (err.kind !== "failed") return false;
  return err.status === undefined || err.status === 404 || err.status >= 500;
}

async function askGemini(key: string, model: string, o: Ready, deadline: number): Promise<string> {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`;
  const data: GeminiResponse = await post(
    url,
    { "x-goog-api-key": key },
    {
      systemInstruction: { parts: [{ text: o.system }] },
      contents: o.messages.map((m) => ({
        role: m.role === "assistant" ? "model" : "user",
        parts: [{ text: m.content }],
      })),
      generationConfig: {
        // Pas de plafond de longueur ici : chez Gemini, le temps de
        // « réflexion » du modèle compte dans ce plafond et peut le vider.
        // La brièveté est demandée par la persona.
        ...(o.temperature !== undefined && { temperature: o.temperature }),
        ...(o.json && { responseMimeType: "application/json" }),
      },
    },
    deadline,
  );

  if (data.promptFeedback?.blockReason) {
    throw new LlmError(`Gemini a bloqué la demande (${data.promptFeedback.blockReason}).`, "blocked");
  }
  const candidate = data.candidates?.[0];
  const text = (candidate?.content?.parts ?? [])
    .filter((p) => !p.thought && typeof p.text === "string")
    .map((p) => p.text)
    .join("")
    .trim();
  if (!text) {
    const reason = candidate?.finishReason ?? "réponse vide";
    const kind = reason === "SAFETY" || reason === "PROHIBITED_CONTENT" ? "blocked" : "failed";
    throw new LlmError(`Gemini n'a rien renvoyé (${reason}).`, kind);
  }
  return text;
}

// ─── Claude ────────────────────────────────────────────────────────────────

type ClaudeResponse = {
  content?: { type: string; text?: string }[];
  stop_reason?: string;
};

async function callClaude(o: Ready): Promise<string> {
  const key = requireEnv("ANTHROPIC_API_KEY");
  const model = process.env.CLAUDE_MODEL?.trim() || DEFAULTS.claude;

  const data: ClaudeResponse = await post(
    "https://api.anthropic.com/v1/messages",
    { "x-api-key": key, "anthropic-version": "2023-06-01" },
    {
      model,
      // Claude exige un plafond : large, pour que l'IA choisisse elle-même la longueur.
      max_tokens: o.maxTokens ?? 4096,
      system: o.json ? `${o.system}\n\nRéponds uniquement avec du JSON valide, sans aucun texte autour.` : o.system,
      messages: o.messages,
      ...(o.temperature !== undefined && { temperature: o.temperature }),
    },
    Date.now() + BUDGET_MS,
  );

  const text = (data.content ?? [])
    .filter((b) => b.type === "text" && typeof b.text === "string")
    .map((b) => b.text)
    .join("")
    .trim();
  if (!text) {
    const kind = data.stop_reason === "refusal" ? "blocked" : "failed";
    throw new LlmError(`Claude n'a rien renvoyé (${data.stop_reason ?? "réponse vide"}).`, kind);
  }
  o.onModel?.(model);
  return text;
}
