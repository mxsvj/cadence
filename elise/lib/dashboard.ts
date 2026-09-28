// Le tableau de bord des gains : les types partagés avec le navigateur, et
// le formatage des montants. Les calculs sont faits dans la base
// (fonction admin_dashboard de supabase/schema.sql).

export type PurchaseKind = "tip" | "message" | "abonnement" | "contenu";

export type DashboardData = {
  genere_le: string;
  jours: number;
  client: string | null;
  /** Des achats de démonstration existent. */
  demo: boolean;
  totaux: {
    depuis_le_debut: number;
    periode: number;
    periode_precedente: number;
    pourboires: { nombre: number; cents: number };
    messages: { nombre: number; achats: number; cents: number };
    contenus: { nombre: number; cents: number };
    abonnements: { actifs: number; nombre: number; cents: number };
  };
  /** La LTV : ce qu'un client rapporte sur toute sa vie (tout l'historique). */
  ltv: {
    clients: number;
    moyenne_cents: number;
    mediane_cents: number;
    max_cents: number;
    achats_par_client: number;
    panier_moyen_cents: number;
    duree_moyenne_jours: number;
    inscrits: number;
    payants: number;
  };
  /** Un point par jour de la période, en centimes. */
  serie: { jour: string; total: number; pourboires: number; messages: number; contenus: number; abonnements: number }[];
  derniers: {
    id: number;
    client: string;
    nom: string;
    type: PurchaseKind;
    quantite: number;
    cents: number;
    date: string;
    demo: boolean;
  }[];
  clients: {
    client: string;
    nom: string;
    demo: boolean;
    pourboires_cents: number;
    pourboires_nombre: number;
    messages_nombre: number;
    messages_cents: number;
    contenus_cents: number;
    contenus_nombre: number;
    abonne: boolean;
    total_cents: number;
    achats: number;
    premier_achat: string;
    dernier_achat: string;
  }[];
};

export const PERIODS = [7, 30, 90] as const;

const euros = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });
const eurosRound = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

/** 1234 → « 12,34 € ». */
export function formatEuros(cents: number): string {
  return euros.format(cents / 100);
}

/** Pour les axes : « 12 € », sans centimes. */
export function formatEurosRound(cents: number): string {
  return eurosRound.format(cents / 100);
}

/** Ce qui a été acheté, en quelques mots. */
export function describePurchase(p: { type: PurchaseKind; quantite: number; cents: number }): string {
  if (p.type === "tip") return `Pourboire de ${formatEuros(p.cents)}`;
  if (p.type === "message") return `${p.quantite} messages achetés · ${formatEuros(p.cents)}`;
  if (p.type === "contenu") return `Contenu débloqué · ${formatEuros(p.cents)}`;
  return `Abonnement mensuel · ${formatEuros(p.cents)}`;
}

/** « à l'instant », « il y a 3 min », « il y a 2 h », puis la date. */
export function timeAgo(iso: string, now: number): string {
  const seconds = Math.max(0, Math.round((now - new Date(iso).getTime()) / 1000));
  if (seconds < 10) return "à l'instant";
  if (seconds < 60) return `il y a ${seconds} s`;
  if (seconds < 3600) return `il y a ${Math.floor(seconds / 60)} min`;
  if (seconds < 86_400) return `il y a ${Math.floor(seconds / 3600)} h`;
  return new Intl.DateTimeFormat("fr-FR", {
    timeZone: "Europe/Paris",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

/** Évolution en % par rapport à la période précédente, ou null si elle était vide. */
export function change(current: number, previous: number): number | null {
  if (previous <= 0) return null;
  return Math.round(((current - previous) / previous) * 100);
}
