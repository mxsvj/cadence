import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { CHAT_TEMPERATURE, LlmError, generate } from "./llm";
import { loadFacts, loadMessages, loadSummary, toTurn } from "./memory";
import { getPersona } from "./persona";
import { chatSystemPrompt, cleanReply, type Turn } from "./prompts";
import { ageFrom, aiMayReply, loadContact, loadProfile, loadSettings, type AiSettings } from "./settings";

// Prendre des nouvelles après une absence. Une fois par jour (tâche planifiée
// de Vercel, voir vercel.json), l'IA écrit un court message amical aux
// personnes absentes depuis le délai choisi par l'équipe. Garde-fous : coupé
// tant que l'équipe ne l'active pas, refusable par chaque personne, un seul
// message par absence, jamais de vente dedans ni juste après (lib/sales.ts),
// jamais de reproche ni de mot qui crée de l'attachement.

/** Personnes traitées au plus par passage (le quota gratuit de Gemini est limité). */
export const RELANCE_BATCH = 25;
/** Au-delà, on s'arrête pour rester dans le temps accordé à la fonction. */
const TIME_BUDGET_MS = 30_000;
/** Messages relus pour écrire la prise de nouvelles. */
const RECENT_MESSAGES = 12;
/** Un secret plus court serait devinable : la tâche reste alors coupée. */
export const MIN_CRON_SECRET = 16;

/** Le secret que Vercel envoie à la tâche planifiée, ou null s'il manque. */
export function cronSecret(): string | null {
  const secret = process.env.CRON_SECRET?.trim();
  return secret && secret.length >= MIN_CRON_SECRET ? secret : null;
}

/** « 2 jours », « 3 jours » : la durée d'absence, arrondie. */
export function absence(hours: number): string {
  const days = Math.max(1, Math.round(hours / 24));
  return days === 1 ? "un jour" : `${days} jours`;
}

/** La consigne propre à la prise de nouvelles, ajoutée à l'instruction habituelle. */
export function relanceTask(hoursAway: number): string {
  return `## Ta tâche maintenant : prendre de ses nouvelles

La personne n'est pas venue depuis ${absence(hoursAway)}. Écris-lui un court message amical, d'une à trois phrases, pour prendre simplement de ses nouvelles. Tu peux rebondir sur un détail de vos échanges (un projet, un moment qu'elle attendait). Si elle t'a parlé de ses proches, d'amis ou d'activités, intéresse-toi à ça : sa vie en dehors d'ici compte plus que cette conversation.

- Aucun reproche, aucune culpabilité, aucune insistance : jamais « tu m'as manqué », « tu m'as oubliée », « pourquoi tu ne viens plus ».
- Rien qui crée de l'attachement ou de la dépendance : elle est libre de revenir ou non, et tu ne le lui demandes pas.
- Aucune vente, aucun contenu, aucune offre, aucune balise.
- Une question légère au plus, ou aucune.
- Tu restes une IA : n'invente pas d'événement de ta vie pour la faire revenir.

Réponds uniquement par le message.`;
}

/** Le message à enregistrer, ou null s'il est vide une fois nettoyé. */
export function cleanRelance(text: string): string | null {
  const clean = cleanReply(text.replace(/\[\[[^\]]*\]\]/g, "")).trim();
  return clean || null;
}

export type RelanceReport = {
  active: boolean;
  sent: number;
  skipped: number;
  failed: number;
  /** Pourquoi le passage s'est arrêté plus tôt (quota, temps). */
  stopped?: string;
};

async function writeRelance(admin: SupabaseClient, userId: string, settings: AiSettings, now: Date): Promise<"sent" | "skipped"> {
  const contact = await loadContact(admin, userId, settings.creator_id);
  // Mode hybride : seulement les personnes à qui l'IA a le droit de répondre.
  if (!aiMayReply(settings, contact)) return "skipped";
  const [profile, facts, summary, recent] = await Promise.all([
    loadProfile(admin, userId),
    loadFacts(admin, userId),
    loadSummary(admin, userId),
    loadMessages(admin, userId, RECENT_MESSAGES),
  ]);
  if (!profile || profile.relances_ok === false || !recent.length) return "skipped";
  const last = recent[recent.length - 1];
  if (last.kind === "relance") return "skipped"; // déjà fait pour cette absence
  const lastSeen = Math.max(new Date(last.created_at).getTime(), profile.vu_le ? new Date(profile.vu_le).getTime() : 0);
  const hoursAway = (now.getTime() - lastSeen) / 3_600_000;

  const system = [
    chatSystemPrompt({
      base: getPersona(),
      persona: settings.creator?.persona ?? {},
      person: {
        name: profile.display_name,
        age: ageFrom(profile.birthdate, now),
        city: contact.city,
        timezone: contact.timezone,
        notes: contact.notes,
        emojiMode: contact.emoji_mode,
        emojis: contact.emojis,
      },
      facts,
      summary: summary?.summary ?? null,
      sale: null,
      extra: settings.extra_instructions,
      now,
    }),
    relanceTask(hoursAway),
  ].join("\n\n");
  const messages: Turn[] = [
    ...recent.map(toTurn),
    { role: "user", content: `(La personne n'est pas revenue depuis ${absence(hoursAway)}. Écris maintenant ton message pour prendre de ses nouvelles.)` },
  ];
  const content = cleanRelance(await generate({ system, messages, temperature: CHAT_TEMPERATURE }));
  if (!content) return "skipped";

  const { error } = await admin
    .from("messages")
    .insert({ user_id: userId, role: "assistant", author: "ai", kind: "relance", content });
  if (error) throw new Error(`Message non enregistré : ${error.message}`);
  return "sent";
}

/** Un passage : trouve les personnes absentes et prend de leurs nouvelles. */
export async function runRelances(admin: SupabaseClient, now: Date = new Date()): Promise<RelanceReport> {
  const started = Date.now();
  const settings = await loadSettings(admin);
  const report: RelanceReport = { active: settings.relance_active && settings.mode !== "manuel", sent: 0, skipped: 0, failed: 0 };
  if (!report.active) return report;

  const { data, error } = await admin.rpc("a_relancer", { p_heures: settings.relance_heures, p_limite: RELANCE_BATCH });
  if (error) throw new Error(`Liste des absences illisible : ${error.message}`);
  for (const { user_id } of (data ?? []) as { user_id: string }[]) {
    if (Date.now() - started > TIME_BUDGET_MS) {
      report.stopped = "temps écoulé : la suite au prochain passage";
      break;
    }
    try {
      report[await writeRelance(admin, user_id, settings, now)]++;
    } catch (err) {
      report.failed++;
      console.error(`Prise de nouvelles impossible (${user_id}) :`, err);
      if (err instanceof LlmError && (err.kind === "rate_limited" || err.kind === "config")) {
        report.stopped = err.kind === "rate_limited" ? "quota du modèle atteint" : err.message;
        break;
      }
    }
  }
  return report;
}
