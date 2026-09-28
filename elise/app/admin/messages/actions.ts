"use server";

import { requireAdmin } from "@/lib/admin";
import { generate } from "@/lib/llm";
import { MESSAGE_COLUMNS, loadMessages, toTurn, type Message } from "@/lib/memory";
import { parseEuros, type Step } from "@/lib/offers";
import { getPersona } from "@/lib/persona";
import { personSection, personaSection } from "@/lib/prompts";
import { ageFrom, loadProfile, type AiSettings } from "@/lib/settings";
import { createClient } from "@/lib/supabase/server";
import { timeZones } from "@/lib/team";

// Ce que l'équipe fait depuis l'onglet Messages. Chaque action vérifie
// d'abord qu'on est administrateur ; la base le revérifie derrière.

type Result<T = object> = ({ ok: true } & T) | { ok: false; error: string };

async function adminClient() {
  const supabase = await createClient();
  await requireAdmin(supabase);
  return supabase;
}

function failure(err: unknown, fallback: string): { ok: false; error: string } {
  const message = (err as { message?: string })?.message;
  console.error(fallback, err);
  return { ok: false, error: message && !message.startsWith("Réservé") ? message : fallback };
}

/** Répondre au nom de l'équipe : le message sera marqué « Équipe ». */
export async function sendTeamMessage(userId: string, text: string): Promise<Result<{ message: Message }>> {
  try {
    const supabase = await adminClient();
    const { data: id, error } = await supabase.rpc("admin_envoyer", { p_user: userId, p_texte: text });
    if (error) throw error;
    const { data, error: readError } = await supabase.from("messages").select(MESSAGE_COLUMNS).eq("id", id).single();
    if (readError) throw readError;
    return { ok: true, message: data as Message };
  } catch (err) {
    return failure(err, "Le message n'est pas parti.");
  }
}

export async function markRead(userId: string): Promise<void> {
  try {
    const supabase = await adminClient();
    await supabase.rpc("admin_marquer_lu", { p_user: userId });
  } catch (err) {
    console.error("Lecture non marquée :", err);
  }
}

export type ContactForm = {
  ai_enabled: boolean;
  city: string;
  timezone: string;
  emojis: string;
  notes: string;
  script_id: number | null;
  spending_cap: string; // en euros, vide = plafond général
};

/** La fiche contact : ce qui aide l'IA à se comporter avec cette personne. */
export async function saveContact(userId: string, form: ContactForm): Promise<Result> {
  try {
    const supabase = await adminClient();
    if (form.notes.length > 5000) return { ok: false, error: "Les notes dépassent 5 000 caractères." };
    if (!timeZones().includes(form.timezone)) return { ok: false, error: "Fuseau horaire inconnu." };
    const cap = form.spending_cap.trim() ? parseEuros(form.spending_cap) : null;
    if (form.spending_cap.trim() && cap === null) return { ok: false, error: "Plafond illisible : indiquez un montant en euros." };
    const { error } = await supabase.from("contacts").upsert(
      {
        user_id: userId,
        ai_enabled: form.ai_enabled,
        city: form.city.trim().slice(0, 120),
        timezone: form.timezone,
        emojis: form.emojis.trim().slice(0, 400),
        notes: form.notes,
        script_id: form.script_id,
        spending_cap_cents: cap,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id" },
    );
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    return failure(err, "La fiche n'a pas été enregistrée.");
  }
}

/** Proposer l'étape suivante, au prix choisi (ramené dans la fourchette par la base). */
export async function proposeNext(
  userId: string,
  stepId: number,
  price: string,
  message: string,
): Promise<Result> {
  try {
    const supabase = await adminClient();
    const cents = price.trim() ? parseEuros(price) : null;
    if (price.trim() && cents === null) return { ok: false, error: "Prix illisible : indiquez un montant en euros." };
    const { error } = await supabase.rpc("admin_proposer", {
      p_user: userId,
      p_step: stepId,
      p_prix_cents: cents,
      p_message: message,
    });
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    return failure(err, "L'offre n'est pas partie.");
  }
}

export async function withdrawOffer(offerId: number): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { error } = await supabase.rpc("admin_retirer_offre", { p_offre: offerId });
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    return failure(err, "L'offre n'a pas été retirée.");
  }
}

/** Faire écrire par l'IA le message qui accompagne une offre ; l'équipe le relit avant l'envoi. */
export async function draftOfferMessage(userId: string, stepId: number, price: string): Promise<Result<{ text: string }>> {
  try {
    const supabase = await adminClient();
    const [{ data: settings }, { data: step }, contact, profile, recent] = await Promise.all([
      supabase.from("ai_settings").select("*").eq("id", 1).single(),
      supabase.from("script_steps").select("*").eq("id", stepId).single(),
      supabase.from("contacts").select("*").eq("user_id", userId).maybeSingle(),
      loadProfile(supabase, userId),
      loadMessages(supabase, userId, 12),
    ]);
    const s = settings as AiSettings;
    const st = step as Step;
    const c = contact.data as { city?: string; timezone?: string; notes?: string; emojis?: string } | null;
    const now = new Date();
    const system = [
      getPersona(),
      personaSection(s.persona ?? {}, { city: c?.city }),
      personSection(
        {
          name: profile?.display_name,
          age: profile ? ageFrom(profile.birthdate, now) : undefined,
          city: c?.city,
          timezone: c?.timezone,
          notes: c?.notes,
          emojis: c?.emojis,
        },
        now,
      ),
      `## Ta tâche\n\nÉcris le court message (une ou deux phrases) qui accompagne l'offre de ce contenu : ${st.ai_description || st.content_type}.${
        st.is_paid ? ` Prix : ${price || (st.price_cents / 100).toFixed(2)} €.` : " C'est un cadeau."
      } Présente-le avec naturel, dans la continuité de la conversation, sans le décrire entièrement. Jamais de pression, jamais en jouant sur la solitude ou l'attachement, aucun sous-entendu sexuel. Réponds uniquement par le message.`,
    ].join("\n\n");
    const text = await generate({
      system,
      messages: recent.map(toTurn),
      temperature: Number(s.temperature ?? 0.8),
      maxTokens: 300,
    });
    return { ok: true, text: text.replace(/\[\[[^\]]*\]\]/g, "").trim() };
  } catch (err) {
    return failure(err, "L'IA n'a pas pu écrire le message.");
  }
}
