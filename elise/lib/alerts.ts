// Les alertes de l'équipe (table team_alerts, voir supabase/schema.sql) :
// les types et leur texte, partagés entre le serveur, la messagerie de
// l'équipe et les messages envoyés sur Discord ou Telegram.

import { formatEuros } from "./dashboard";
import { URGENCY_LABEL, type UrgencyReason } from "./urgency";

export type AlertKind = "contre_offre" | "plafond" | "urgence";

export type AlertDetail = {
  /** urgence */
  raison?: UrgencyReason;
  source?: "mots" | "ia";
  /** contre_offre */
  montant_cents?: number;
  prix_cents?: number;
  statut?: "acceptee" | "refusee";
  essais_restants?: number | null;
  /** plafond */
  depense_cents?: number;
  plafond_cents?: number;
};

export type TeamAlert = {
  id: number;
  kind: AlertKind;
  user_id: string;
  creator_id: number;
  offer_id?: number | null;
  /** Le prénom de la personne (jamais envoyé sur Discord ou Telegram). */
  nom?: string;
  creatrice: string;
  detail: AlertDetail;
  /** Date de l'alerte (admin_alertes) ; created_at dans la table. */
  date?: string;
  created_at?: string;
};

/** À partir de ce pourcentage du plafond du mois dépensé, l'équipe est prévenue (même seuil que schema.sql). */
export const NEAR_CAP_PERCENT = 80;

/** Le plafond du mois est-il presque atteint (ou atteint) ? */
export function nearCap(spentCents: number, capCents: number | null): boolean {
  return capCents !== null && capCents > 0 && spentCents * 100 >= capCents * NEAR_CAP_PERCENT;
}

export const ALERT_TITLE: Record<AlertKind, string> = {
  urgence: "Urgence",
  contre_offre: "Contre-offre",
  plafond: "Plafond bientôt atteint",
};

/** Du plus pressant au moins pressant, pour trier et pour les pastilles. */
export const ALERT_ORDER: AlertKind[] = ["urgence", "contre_offre", "plafond"];

/** Ce qui s'est passé, en une phrase, sans le texte des messages. */
export function alertSummary(alert: Pick<TeamAlert, "kind" | "detail">): string {
  const d = alert.detail ?? {};
  switch (alert.kind) {
    case "urgence":
      return URGENCY_LABEL[d.raison ?? "attention"] ?? URGENCY_LABEL.attention;
    case "contre_offre": {
      const amount = d.montant_cents !== undefined ? formatEuros(d.montant_cents) : "un montant";
      const price = d.prix_cents !== undefined ? ` pour un prix de ${formatEuros(d.prix_cents)}` : "";
      const outcome =
        d.statut === "acceptee"
          ? "acceptée"
          : `refusée${typeof d.essais_restants === "number" ? `, encore ${d.essais_restants} essai${d.essais_restants > 1 ? "s" : ""}` : ""}`;
      return `Propose ${amount}${price} (${outcome})`;
    }
    case "plafond":
      return d.depense_cents !== undefined && d.plafond_cents !== undefined
        ? `${formatEuros(d.depense_cents)} dépensés sur ${formatEuros(d.plafond_cents)} ce mois-ci : l'IA ne propose plus de contenu payant`
        : "Plafond du mois bientôt atteint : l'IA ne propose plus de contenu payant";
  }
}

/** La conversation, dans l'onglet Messages. */
export function alertPath(alert: Pick<TeamAlert, "user_id" | "creator_id">): string {
  return `/admin/messages?u=${alert.user_id}&c=${alert.creator_id}`;
}

const ICON: Record<AlertKind, string> = { urgence: "🔴", contre_offre: "💬", plafond: "🟠" };

/**
 * Le message envoyé sur Discord ou Telegram : le type d'alerte, la créatrice,
 * la phrase et le lien. Jamais le prénom, l'e-mail ni le texte des messages.
 */
export function alertMessage(alert: Pick<TeamAlert, "kind" | "detail" | "creatrice" | "user_id" | "creator_id">, origin: string): string {
  return [
    `${ICON[alert.kind]} ${ALERT_TITLE[alert.kind]} · conversation avec ${alert.creatrice}`,
    alertSummary(alert),
    `Ouvrir : ${origin.replace(/\/+$/, "")}${alertPath(alert)}`,
  ].join("\n");
}
