import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { schemaOutdated } from "./admin";
import type { AlertKind, TeamAlert } from "./alerts";
import { MESSAGE_COLUMNS, type Message } from "./memory";
import type { Script, Step } from "./offers";
import { displayName } from "./persona-profile";
import { describeBlock, loadSaleContext } from "./sales";
import { loadContact, loadCreator, loadSettings, type AiMode, type Contact } from "./settings";
import { createAdminClient } from "./supabase/admin";

// Ce que voit l'équipe dans l'onglet « Messages » : une conversation par
// personne et par créatrice. Tout est lu avec la session de
// l'administrateur : la base (RLS et fonctions admin_*) vérifie elle-même
// qu'il en est bien un.

export type InboxItem = {
  user_id: string;
  creator_id: number;
  /** Le prénom de la créatrice de cette conversation. */
  creatrice: string;
  email: string;
  nom: string;
  dernier: { id: number; auteur: "user" | "ai" | "team"; type: "text" | "offer" | "relance"; texte: string; date: string };
  non_lus: number;
  ia_autorisee: boolean;
  /** L'équipe a pris la main : l'IA se tait dans cette conversation (absent avant schema.sql relancé). */
  manuel?: boolean;
  /** Les alertes à traiter dans cette conversation (absent avant schema.sql relancé). */
  alertes?: AlertKind[];
  depense_cents: number;
};

export type Person = {
  user_id: string;
  email: string;
  nom: string;
  age: number | null;
  inscrit_le: string;
  depense_cents: number;
  depense_mois_cents: number;
  script_id: number | null;
  prochaine_etape: Step | null;
};

export type TeamOffer = {
  id: number;
  step_id: number | null;
  content_type: Step["content_type"];
  photo_count: number;
  video_count: number;
  price_cents: number;
  personalized: boolean;
  status: "proposee" | "achetee" | "offerte" | "retiree";
  proposed_by: "ai" | "team";
  bids_refused: number;
  last_bid_cents: number | null;
  last_bid_status: "acceptee" | "refusee" | null;
  created_at: string;
  purchased_at: string | null;
};

export type Thread = {
  person: Person;
  contact: Contact;
  /** La créatrice de cette conversation (son IA autorisée et ses emojis sont dans la fiche). */
  creatorId: number;
  creatorName: string;
  /** En ligne : les personnes peuvent la choisir, et l'IA leur répond. */
  creatorActive: boolean;
  /** Où en est la vente : « Prochaine offre dans 3 messages. », etc. */
  sale: string;
  /** Les alertes à traiter dans cette conversation, les plus récentes d'abord. */
  alerts: TeamAlert[];
  messages: Message[];
  offers: TeamOffer[];
  steps: Record<number, Pick<Step, "id" | "title" | "content_type">>;
  scripts: Script[];
  facts: string[];
};

function check<T>(r: { data: T | null; error: { message: string } | null }, what: string): T {
  if (r.error) throw new Error(`${what} : ${r.error.message}`);
  return r.data as T;
}

/** Les alertes à traiter, pour le bandeau de l'espace de l'équipe (null : schema.sql pas encore relancé). */
export async function loadAlerts(supabase: SupabaseClient): Promise<TeamAlert[] | null> {
  const { data, error } = await supabase.rpc("admin_alertes");
  if (error) {
    if (schemaOutdated(error)) return null;
    throw new Error(`Alertes illisibles : ${error.message}`);
  }
  return ((data ?? []) as TeamAlert[]).map((a) => ({ ...a, creator_id: Number(a.creator_id) }));
}

export async function loadInbox(supabase: SupabaseClient): Promise<{ mode: AiMode; conversations: InboxItem[] }> {
  const [list, settings] = await Promise.all([
    supabase.rpc("admin_boite"),
    supabase.from("ai_settings").select("mode").eq("id", 1).maybeSingle(),
  ]);
  return {
    conversations: check(list, "Conversations illisibles") as InboxItem[],
    mode: ((check(settings, "Réglages illisibles") as { mode: AiMode } | null)?.mode ?? "auto") as AiMode,
  };
}

export async function loadThread(supabase: SupabaseClient, userId: string, creatorId: number): Promise<Thread | null> {
  const [person, settings, creator, messages, offers, scripts, facts, contact, alerts] = await Promise.all([
    supabase.rpc("admin_personne", { p_user: userId, p_creator: creatorId }),
    loadSettings(supabase),
    loadCreator(supabase, creatorId),
    supabase
      .from("messages")
      .select(MESSAGE_COLUMNS)
      .eq("user_id", userId)
      .eq("creator_id", creatorId)
      .order("id", { ascending: false })
      .limit(300),
    supabase.from("offers").select("*").eq("user_id", userId).eq("creator_id", creatorId).order("id"),
    // « * » : creator_id n'existe qu'une fois schema.sql relancé.
    supabase.from("scripts").select("*").order("position").order("id"),
    supabase.from("user_facts").select("fact").eq("user_id", userId).eq("creator_id", creatorId).order("id"),
    // La fiche, avec ce que cette créatrice fait avec cette personne.
    loadContact(supabase, userId, creatorId),
    supabase
      .from("team_alerts")
      .select("id, kind, user_id, creator_id, offer_id, detail, created_at")
      .eq("user_id", userId)
      .eq("creator_id", creatorId)
      .is("handled_at", null)
      .order("created_at", { ascending: false }),
  ]);
  // Tant que schema.sql n'est pas relancé, la table des alertes n'existe pas.
  if (alerts.error) console.error("Alertes illisibles :", alerts.error.message);
  const p = check(person, "Personne introuvable") as Person | null;
  if (!p || !creator) return null;
  // Où en est la vente, et pourquoi l'IA ne propose pas (lu avec la clé
  // secrète : les fonctions de vente sont réservées au serveur).
  let sale = "";
  try {
    const context = await loadSaleContext(createAdminClient(), userId, creatorId, settings, false);
    sale = describeBlock(context.block, context.next);
  } catch (err) {
    console.error("État de la vente illisible :", err);
  }

  const offerRows = check(offers, "Offres illisibles") as TeamOffer[];
  const stepIds = [...new Set(offerRows.map((o) => o.step_id).filter((id): id is number => id !== null))];
  const steps: Thread["steps"] = {};
  if (stepIds.length) {
    const rows = check(
      await supabase.from("script_steps").select("id, title, content_type").in("id", stepIds),
      "Étapes illisibles",
    ) as Thread["steps"][number][];
    for (const s of rows) steps[s.id] = s;
  }

  return {
    person: p,
    contact,
    creatorId,
    creatorName: displayName(creator.persona),
    creatorActive: creator.active,
    sale,
    alerts: ((alerts.data ?? []) as Omit<TeamAlert, "creatrice">[]).map((a) => ({
      ...a,
      creator_id: Number(a.creator_id),
      creatrice: displayName(creator.persona),
    })),
    messages: (check(messages, "Messages illisibles") as Message[]).reverse(),
    offers: offerRows,
    steps,
    scripts: usableScripts(check(scripts, "Scripts illisibles") as Script[], creatorId, contact.script_id),
    facts: (check(facts, "Fiche illisible") as { fact: string }[]).map((f) => f.fact),
  };
}

/**
 * Les scripts qu'on peut choisir dans la fiche : ceux de la créatrice de la
 * conversation et ceux qui servent à toutes. Celui déjà choisi reste visible, signalé,
 * s'il est à une autre créatrice (l'IA ne s'en sert pas).
 */
export function usableScripts(scripts: Script[], activeCreator: number | null, chosen: number | null): Script[] {
  return scripts.flatMap((s) => {
    const owner = s.creator_id == null ? null : Number(s.creator_id);
    if (owner === null || owner === activeCreator) return [{ ...s, creator_id: owner }];
    if (s.id === chosen) return [{ ...s, creator_id: owner, name: `${s.name} (autre créatrice : pas utilisé)` }];
    return [];
  });
}

/** Les fuseaux horaires que connaît le navigateur ou le serveur. */
export function timeZones(): string[] {
  try {
    return Intl.supportedValuesOf("timeZone");
  } catch {
    return ["Europe/Paris"];
  }
}
