import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { after } from "next/server";
import { alertMessage, type TeamAlert } from "./alerts";
import { createAdminClient } from "./supabase/admin";
import type { UrgencyReason } from "./urgency";

// Prévenir l'équipe : créer une alerte d'urgence, et envoyer les nouvelles
// alertes sur Discord ou Telegram si l'équipe l'a branché (variables
// d'environnement, gratuites toutes les deux). Sans ça, les alertes restent
// visibles dans l'espace de l'équipe (bandeau et onglet Messages). Un envoi
// raté ne bloque jamais la conversation.

/** Alertes envoyées au plus par passage. */
const BATCH = 10;
const TIMEOUT_MS = 5000;

const DISCORD = /^https:\/\/(?:(?:ptb|canary)\.)?discord(?:app)?\.com\/api\/webhooks\/\d+\/[\w-]+$/;
const TELEGRAM_TOKEN = /^\d+:[\w-]{30,}$/;
const TELEGRAM_CHAT = /^(?:-?\d+|@\w{5,})$/;

type Channels = { discord: string | null; telegram: { token: string; chat: string } | null };

/** Les canaux branchés (null : absent ou mal copié). */
export function alertChannels(): Channels {
  const discord = process.env.DISCORD_WEBHOOK_URL?.trim() ?? "";
  const token = process.env.TELEGRAM_BOT_TOKEN?.trim() ?? "";
  const chat = process.env.TELEGRAM_CHAT_ID?.trim() ?? "";
  return {
    discord: DISCORD.test(discord) ? discord : null,
    telegram: TELEGRAM_TOKEN.test(token) && TELEGRAM_CHAT.test(chat) ? { token, chat } : null,
  };
}

/** Ce que l'onglet Paramètres affiche : branché, absent, ou rempli mais illisible. */
export function channelStatus(): { discord: "ok" | "absent" | "invalide"; telegram: "ok" | "absent" | "invalide" } {
  const channels = alertChannels();
  const filled = (name: string) => Boolean(process.env[name]?.trim());
  return {
    discord: channels.discord ? "ok" : filled("DISCORD_WEBHOOK_URL") ? "invalide" : "absent",
    telegram: channels.telegram
      ? "ok"
      : filled("TELEGRAM_BOT_TOKEN") || filled("TELEGRAM_CHAT_ID")
        ? "invalide"
        : "absent",
  };
}

async function post(url: string, body: unknown): Promise<void> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
}

/** Envoie les alertes pas encore envoyées. Renvoie le nombre d'alertes parties. */
export async function flushAlerts(admin: SupabaseClient, origin: string): Promise<number> {
  const channels = alertChannels();
  if (!channels.discord && !channels.telegram) return 0;
  const { data, error } = await admin.rpc("alertes_a_envoyer", { p_limite: BATCH });
  if (error) {
    console.error("Alertes illisibles :", error.message);
    return 0;
  }
  let sent = 0;
  for (const alert of (data ?? []) as TeamAlert[]) {
    const text = alertMessage(alert, origin);
    const sends: Promise<void>[] = [];
    // Aucune mention (@everyone…) ne peut partir, quoi que contienne le texte.
    if (channels.discord) sends.push(post(channels.discord, { content: text, allowed_mentions: { parse: [] } }));
    if (channels.telegram) {
      sends.push(
        post(`https://api.telegram.org/bot${channels.telegram.token}/sendMessage`, {
          chat_id: channels.telegram.chat,
          text,
          disable_web_page_preview: true,
        }),
      );
    }
    const results = await Promise.allSettled(sends);
    // Jamais l'adresse du webhook ni le jeton Telegram dans les journaux.
    for (const r of results) if (r.status === "rejected") console.error("Alerte non envoyée :", (r.reason as Error)?.message ?? "erreur");
    if (results.some((r) => r.status === "fulfilled")) sent++;
  }
  return sent;
}

/**
 * Une fois la réponse partie (la personne n'attend pas) : envoie les alertes
 * en attente. À appeler depuis une route après une action qui peut en créer.
 */
export function flushAlertsLater(origin: string): void {
  const channels = alertChannels();
  if (!channels.discord && !channels.telegram) return;
  after(async () => {
    try {
      await flushAlerts(createAdminClient(), origin);
    } catch (err) {
      console.error("Envoi des alertes impossible :", (err as Error)?.message ?? err);
    }
  });
}

/** Une personne a besoin d'un humain : alerte d'urgence (une seule à la fois par conversation). */
export async function raiseUrgency(
  admin: SupabaseClient,
  userId: string,
  creatorId: number,
  reason: UrgencyReason,
  source: "mots" | "ia",
): Promise<boolean> {
  const { data, error } = await admin.rpc("alerter_equipe", {
    p_user: userId,
    p_creator: creatorId,
    p_kind: "urgence",
    p_offer: null,
    p_detail: { raison: reason, source },
  });
  if (error) {
    console.error("Alerte d'urgence non créée :", error.message);
    return false;
  }
  return data !== null;
}
