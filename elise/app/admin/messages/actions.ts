"use server";

import { SCHEMA_HINT, requireAdmin, schemaOutdated } from "@/lib/admin";
import { cleanEmojis, isEmojiMode, type EmojiMode } from "@/lib/emojis";
import { CHAT_TEMPERATURE, generate } from "@/lib/llm";
import { MESSAGE_COLUMNS, loadMessages, toTurn, type Message } from "@/lib/memory";
import { describeStep, parseEuros, type Step } from "@/lib/offers";
import { getPersona } from "@/lib/persona";
import { personSection, personaSection } from "@/lib/prompts";
import { ageFrom, loadContact, loadCreator, loadProfile } from "@/lib/settings";
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
  if (schemaOutdated(err)) return { ok: false, error: `${fallback.replace(/\.$/, "")} : ${SCHEMA_HINT}` };
  return { ok: false, error: message && !message.startsWith("Réservé") ? message : fallback };
}

/** Répondre au nom de l'équipe, dans cette conversation : le message sera marqué « Équipe ». */
export async function sendTeamMessage(userId: string, creatorId: number, text: string): Promise<Result<{ message: Message }>> {
  try {
    const supabase = await adminClient();
    const { data: id, error } = await supabase.rpc("admin_envoyer", { p_user: userId, p_creator: creatorId, p_texte: text });
    if (error) throw error;
    const { data, error: readError } = await supabase.from("messages").select(MESSAGE_COLUMNS).eq("id", id).single();
    if (readError) throw readError;
    return { ok: true, message: data as Message };
  } catch (err) {
    return failure(err, "Le message n'est pas parti.");
  }
}

export async function markRead(userId: string, creatorId: number): Promise<void> {
  try {
    const supabase = await adminClient();
    await supabase.rpc("admin_marquer_lu", { p_user: userId, p_creator: creatorId });
  } catch (err) {
    console.error("Lecture non marquée :", err);
  }
}

export type ContactForm = {
  ai_enabled: boolean;
  city: string;
  timezone: string;
  emoji_mode: EmojiMode;
  emojis: string;
  notes: string;
  script_id: number | null;
  spending_cap: string; // en euros, vide = plafond général
};

/**
 * La fiche contact : ce qui aide l'IA à se comporter avec cette personne
 * (commun à toutes les créatrices), et ce que la créatrice de cette
 * conversation fait avec elle (IA autorisée, emojis).
 */
export async function saveContact(userId: string, creatorId: number, form: ContactForm): Promise<Result> {
  try {
    const supabase = await adminClient();
    if (form.notes.length > 5000) return { ok: false, error: "Les notes dépassent 5 000 caractères." };
    if (!timeZones().includes(form.timezone)) return { ok: false, error: "Fuseau horaire inconnu." };
    const cap = form.spending_cap.trim() ? parseEuros(form.spending_cap) : null;
    if (form.spending_cap.trim() && cap === null) return { ok: false, error: "Plafond illisible : indiquez un montant en euros." };
    const now = new Date().toISOString();
    const { error } = await supabase.from("contacts").upsert(
      {
        user_id: userId,
        city: form.city.trim().slice(0, 120),
        timezone: form.timezone,
        notes: form.notes,
        script_id: form.script_id,
        spending_cap_cents: cap,
        updated_at: now,
      },
      { onConflict: "user_id" },
    );
    if (error) throw error;
    // IA autorisée et emojis : ceux de la créatrice de cette conversation.
    {
      const { error: creatorError } = await supabase.from("creator_contacts").upsert(
        {
          creator_id: creatorId,
          user_id: userId,
          ai_enabled: form.ai_enabled,
          emoji_mode: isEmojiMode(form.emoji_mode) ? form.emoji_mode : "libre",
          emojis: cleanEmojis(form.emojis),
          updated_at: now,
        },
        { onConflict: "creator_id,user_id" },
      );
      if (creatorError) throw creatorError;
    }
    return { ok: true };
  } catch (err) {
    return failure(err, "La fiche n'a pas été enregistrée.");
  }
}

/** Proposer l'étape suivante, au prix choisi (ramené dans la fourchette par la base). */
export async function proposeNext(
  userId: string,
  creatorId: number,
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
      p_creator: creatorId,
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
export async function draftOfferMessage(
  userId: string,
  creatorId: number,
  stepId: number,
  price: string,
): Promise<Result<{ text: string }>> {
  try {
    const supabase = await adminClient();
    const [creator, { data: step }, profile, recent, c] = await Promise.all([
      loadCreator(supabase, creatorId),
      supabase.from("script_steps").select("*").eq("id", stepId).single(),
      loadProfile(supabase, userId),
      loadMessages(supabase, userId, creatorId, 12),
      // La fiche de la personne, avec les réglages de cette créatrice.
      loadContact(supabase, userId, creatorId),
    ]);
    if (!creator) return { ok: false, error: "Cette créatrice n'existe plus." };
    const st = step as Step;
    const now = new Date();
    const system = [
      getPersona(),
      personaSection(creator.persona, { city: c.city }),
      personSection(
        {
          name: profile?.display_name,
          age: profile ? ageFrom(profile.birthdate, now) : undefined,
          city: c.city,
          timezone: c.timezone,
          notes: c.notes,
          emojiMode: c.emoji_mode,
          emojis: c.emojis,
        },
        now,
      ),
      `## Ta tâche\n\nÉcris le court message (une ou deux phrases) qui accompagne l'offre de ce contenu : ${describeStep(st)}.${
        st.is_paid ? ` Prix : ${price || (st.price_cents / 100).toFixed(2)} €.` : " C'est un cadeau."
      }${
        st.message_mode === "ia" && st.message_text.trim()
          ? ` Ce que l'équipe veut que tu dises, à reformuler avec tes mots, sans rien y ajouter : « ${st.message_text.trim()} ».`
          : ""
      } Présente-le avec naturel, dans la continuité de la conversation, sans le décrire entièrement. Jamais de pression, jamais en jouant sur la solitude ou l'attachement, aucun sous-entendu sexuel. Réponds uniquement par le message.`,
    ].join("\n\n");
    const text = await generate({
      system,
      messages: recent.map(toTurn),
      temperature: CHAT_TEMPERATURE,
    });
    return { ok: true, text: text.replace(/\[\[[^\]]*\]\]/g, "").trim() };
  } catch (err) {
    return failure(err, "L'IA n'a pas pu écrire le message.");
  }
}
