import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { isSensitive } from "./facts";
import { generate, lightModel } from "./llm";
import { crossed } from "./memory";
import { transcript, type Turn } from "./prompts";

// Le profil de discussion : tous les PROFILE_EVERY messages de la personne,
// un petit modèle relit la fin de la conversation et note, sans rien dire,
// son humeur du moment, le sujet qui lui plaît et sa façon d'écrire. Ces
// trois mots vont dans sa fiche (contacts) et dans la consigne du message
// suivant, pour adapter le ton. Jamais pour vendre.

export const PROFILE_EVERY = 5;
export const MOODS = ["joyeux", "en forme", "neutre", "fatigué", "stressé"] as const;
export const STYLES = ["timide", "joueur", "direct"] as const;
const MAX_INTEREST = 80;

export type DiscussionProfile = { humeur: string; style: string; interet: string };

/** Faut-il relire la conversation après ces messages de la personne ? */
export function profileDue(userMessages: number, added = 1): boolean {
  return crossed(userMessages, added, PROFILE_EVERY);
}

export function profileSystemPrompt(): string {
  return `Tu relis la fin d'une conversation entre une personne et une créatrice (une IA). Note, à partir des messages de la PERSONNE seulement :
- "humeur" : son humeur du moment, un seul de ces mots : ${MOODS.join(", ")} ; "" si on ne peut pas savoir ;
- "style" : sa façon d'écrire, un seul de ces mots : ${STYLES.join(", ")} (timide : réservé, peu sûr de lui ; joueur : taquin, blagueur ; direct : messages courts, droit au but) ; "" si on ne peut pas savoir ;
- "centre_interet" : le sujet qui lui plaît le plus dans ces messages, en 2 à 6 mots (« la randonnée », « son chien », « les séries policières ») ; "" s'il n'y en a pas.

JAMAIS rien sur la santé (physique ou mentale), la religion, l'orientation sexuelle ou la vie intime, l'argent : dans ces cas, laisse "".

Réponds uniquement en JSON : {"humeur": "…", "style": "…", "centre_interet": "…"}`;
}

/** Lit la réponse du modèle : seulement des valeurs de la liste, un sujet court et sans donnée sensible. */
export function parseProfile(raw: string): DiscussionProfile {
  const empty = { humeur: "", style: "", interet: "" };
  const match = raw.match(/\{[\s\S]*\}/);
  if (!match) return empty;
  try {
    const data = JSON.parse(match[0]) as Record<string, unknown>;
    const pick = (value: unknown, allowed: readonly string[]) => {
      const v = typeof value === "string" ? value.trim().toLowerCase() : "";
      return allowed.includes(v) ? v : "";
    };
    let interet = typeof data.centre_interet === "string" ? data.centre_interet.replace(/\s+/g, " ").trim() : "";
    if (interet.length > MAX_INTEREST || isSensitive(interet)) interet = "";
    return { humeur: pick(data.humeur, MOODS), style: pick(data.style, STYLES), interet };
  } catch {
    return empty;
  }
}

/** Relit la fin de la conversation et met la fiche à jour. Ce qui n'est pas sûr reste inchangé. */
export async function updateDiscussionProfile(admin: SupabaseClient, userId: string, recent: Turn[], now = new Date()): Promise<DiscussionProfile> {
  const raw = await generate({
    system: profileSystemPrompt(),
    messages: [{ role: "user", content: transcript(recent.slice(-2 * PROFILE_EVERY)) }],
    temperature: 0,
    maxTokens: 200,
    json: true,
    model: lightModel(),
  });
  const profile = parseProfile(raw);
  const row: Record<string, unknown> = { user_id: userId, profil_maj_le: now.toISOString() };
  if (profile.humeur) row.humeur = profile.humeur;
  if (profile.style) row.style_discussion = profile.style;
  if (profile.interet) row.centre_interet = profile.interet;
  const { error } = await admin.from("contacts").upsert(row, { onConflict: "user_id" });
  if (error) throw new Error(`Profil de discussion non enregistré : ${error.message}`);
  return profile;
}
