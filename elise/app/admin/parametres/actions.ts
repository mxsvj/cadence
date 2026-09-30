"use server";

import { SCHEMA_HINT, requireAdmin, schemaOutdated } from "@/lib/admin";
import { buildReply } from "@/lib/conversation";
import { CHAT_TEMPERATURE, generate } from "@/lib/llm";
import { displayName } from "@/lib/persona-profile";
import { cleanReply } from "@/lib/prompts";
import { loadContact, loadCreator, loadProfile, loadSettings } from "@/lib/settings";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// L'onglet Paramètres : les réglages fins de l'IA (mémoire, consignes) et les
// garde-fous de la vente. L'action vérifie d'abord qu'on est administrateur ; la base le
// revérifie (règles de sécurité).

type Result = { ok: true } | { ok: false; error: string };

export type ParametersForm = {
  context_messages: number;
  extra_instructions: string;
  sales_min_messages: number;
  sales_gap_messages: number;
  /** Prendre des nouvelles : envoyé seulement si le réglage a changé. */
  relance?: { active: boolean; hours: number };
};

const between = (n: number, min: number, max: number) => Number.isFinite(n) && n >= min && n <= max;

export async function saveParameters(form: ParametersForm): Promise<Result> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    if (!between(form.context_messages, 6, 60)) return { ok: false, error: "Entre 6 et 60 messages relus." };
    if (!between(form.sales_min_messages, 0, 1000) || !between(form.sales_gap_messages, 0, 1000)) {
      return { ok: false, error: "Nombres de messages invalides." };
    }
    if (form.extra_instructions.length > 5000) return { ok: false, error: "Consignes trop longues (5 000 caractères)." };
    if (form.relance && !between(form.relance.hours, 24, 336)) return { ok: false, error: "Délai d'absence : entre 24 heures et 2 semaines." };

    const { error } = await supabase
      .from("ai_settings")
      .update({
        context_messages: Math.round(form.context_messages),
        extra_instructions: form.extra_instructions.trim(),
        sales_min_messages: Math.round(form.sales_min_messages),
        sales_gap_messages: Math.round(form.sales_gap_messages),
        ...(form.relance ? { relance_active: Boolean(form.relance.active), relance_heures: Math.round(form.relance.hours) } : {}),
        updated_at: new Date().toISOString(),
      })
      .eq("id", 1);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error("Paramètres non enregistrés :", err);
    if (schemaOutdated(err)) return { ok: false, error: `Les paramètres n'ont pas été enregistrés : ${SCHEMA_HINT}` };
    return { ok: false, error: "Les paramètres n'ont pas été enregistrés." };
  }
}

export type AiCheck = {
  creatrice: string;
  ok: boolean;
  /** Durée de l'essai, en millisecondes. */
  ms: number;
  /** Le modèle qui a répondu (le principal, ou celui de secours). */
  model?: string;
  text?: string;
  error?: string;
};

const TEST_MESSAGE = "Salut ! Tu fais quoi de beau aujourd'hui ?";

/**
 * « Tester l'IA » : pour chaque créatrice en ligne, prépare une vraie réponse
 * (consigne, mémoire, vente) et la demande au modèle, sans rien enregistrer.
 * Donne l'erreur exacte si ça coince, pour savoir où chercher.
 */
export async function testAi(): Promise<{ ok: true; checks: AiCheck[] } | { ok: false; error: string }> {
  let userId: string | null;
  let supabase: Awaited<ReturnType<typeof createClient>>;
  try {
    supabase = await createClient();
    await requireAdmin(supabase);
    userId = await currentUserId(supabase);
  } catch {
    return { ok: false, error: "Réservé à l'équipe." };
  }
  if (!userId) return { ok: false, error: "Session expirée." };
  const me = userId;

  let admin: ReturnType<typeof createAdminClient>;
  try {
    admin = createAdminClient();
  } catch (err) {
    return { ok: false, error: (err as Error).message };
  }
  try {
    const [settings, online, profile] = await Promise.all([
      loadSettings(admin),
      admin.from("creators").select("id").eq("active", true).order("id"),
      loadProfile(supabase, me).catch(() => null),
    ]);
    if (online.error) throw new Error(`Créatrices illisibles : ${online.error.message}`);
    const ids = ((online.data ?? []) as { id: number }[]).map((c) => Number(c.id));
    if (ids.length === 0) return { ok: false, error: "Aucune créatrice en ligne : mettez-en une en ligne dans l'onglet IA." };

    const checks = await Promise.all(
      ids.map(async (id): Promise<AiCheck> => {
        const started = Date.now();
        let creatrice = `Créatrice n° ${id}`;
        let model: string | undefined;
        try {
          const creator = await loadCreator(admin, id);
          if (!creator) throw new Error("Créatrice introuvable.");
          creatrice = displayName(creator.persona);
          const contact = await loadContact(admin, me, id);
          const context = await buildReply({ supabase, admin, userId: me, creator, newMessage: TEST_MESSAGE, now: new Date(), settings, contact, profile });
          const reply = await generate({
            system: context.system,
            messages: context.messages,
            temperature: CHAT_TEMPERATURE,
            onModel: (m) => (model = m),
          });
          return { creatrice, ok: true, ms: Date.now() - started, model, text: cleanReply(reply).slice(0, 400) };
        } catch (err) {
          console.error(`Tester l'IA (${creatrice}) :`, err);
          const message = err instanceof Error ? err.message : String(err);
          return { creatrice, ok: false, ms: Date.now() - started, error: message.slice(0, 600) };
        }
      }),
    );
    return { ok: true, checks };
  } catch (err) {
    console.error("Tester l'IA :", err);
    return { ok: false, error: `${(err as Error).message}`.slice(0, 600) };
  }
}
