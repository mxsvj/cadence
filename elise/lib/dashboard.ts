// Le tableau de bord des gains : les types partagés avec le navigateur, et
// le formatage des montants. Les calculs sont faits dans la base
// (fonction admin_dashboard de supabase/schema.sql).

export type PurchaseKind = "tip" | "message" | "abonnement" | "contenu";

export type DashboardData = {
  genere_le: string;
  /** La période affichée (AAAA-MM-JJ, heure de Paris), et sa durée en jours. */
  debut?: string;
  fin?: string;
  jours: number;
  /** Un point de la courbe par jour, semaine ou mois. */
  pas?: "jour" | "semaine" | "mois";
  /** Montants nets des frais de paiement estimés. */
  net?: boolean;
  /** La créatrice choisie (null : toutes), et toutes les créatrices pour la liste. */
  createur?: number | null;
  createurs?: { id: number; nom: string }[];
  /** Des achats de démonstration existent. */
  demo: boolean;
  /** La base n'a pas encore été mise à jour : filtres réduits. */
  outdated?: boolean;
  totaux: {
    depuis_le_debut: number;
    periode: number;
    /** null : rien à comparer (« depuis le début »). */
    periode_precedente: number | null;
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
  };
  /** Combien de clients dans chaque tranche de LTV. */
  repartition?: { min_cents: number; max_cents: number | null; clients: number }[];
  /** Un point par jour, semaine ou mois de la période (date de son début), en centimes. */
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
    createur?: string | null;
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

// ─── Les périodes ───────────────────────────────────────────────────────────

export type PeriodKey = "aujourdhui" | "hier" | "7j" | "30j" | "90j" | "6m" | "1a" | "tout" | "dates";

export const PERIOD_OPTIONS: { key: PeriodKey; label: string }[] = [
  { key: "aujourdhui", label: "Aujourd'hui" },
  { key: "hier", label: "Hier" },
  { key: "7j", label: "7 derniers jours" },
  { key: "30j", label: "30 derniers jours" },
  { key: "90j", label: "90 derniers jours" },
  { key: "6m", label: "6 derniers mois" },
  { key: "1a", label: "12 derniers mois" },
  { key: "tout", label: "Depuis le début" },
  { key: "dates", label: "Dates précises…" },
];

/** Ce que l'équipe a choisi en haut du tableau de bord. */
export type DashboardFilters = {
  period: PeriodKey;
  /** Pour « Dates précises » : du … au … (AAAA-MM-JJ). */
  from?: string;
  to?: string;
  creator: number | null;
  net: boolean;
};

export const DEFAULT_FILTERS: DashboardFilters = { period: "30j", creator: null, net: false };

/** Frais de paiement estimés pour le net : tarif Stripe des cartes européennes. */
export const NET_FEES = "1,5 % + 0,25 € par achat (tarif Stripe des cartes européennes)";

const ISO = /^\d{4}-\d{2}-\d{2}$/;

export function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !ISO.test(value)) return false;
  const d = new Date(`${value}T12:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === value;
}

/** Aujourd'hui, à Paris (AAAA-MM-JJ). */
export function parisToday(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Paris", year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
}

export function addDays(iso: string, days: number): string {
  const d = new Date(`${iso}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

/** Le même jour, N mois plus tôt ou plus tard (le 31 devient le dernier jour du mois). */
export function addMonths(iso: string, months: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const target = new Date(Date.UTC(y, m - 1 + months, 1, 12));
  const last = new Date(Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0, 12)).getUTCDate();
  target.setUTCDate(Math.min(d, last));
  return target.toISOString().slice(0, 10);
}

/**
 * Les dates de la période (debut null : depuis le premier achat), ou null
 * si les dates précises sont incomplètes ou à l'envers.
 */
export function periodRange(f: Pick<DashboardFilters, "period" | "from" | "to">, today: string): { debut: string | null; fin: string } | null {
  switch (f.period) {
    case "aujourdhui":
      return { debut: today, fin: today };
    case "hier":
      return { debut: addDays(today, -1), fin: addDays(today, -1) };
    case "7j":
      return { debut: addDays(today, -6), fin: today };
    case "30j":
      return { debut: addDays(today, -29), fin: today };
    case "90j":
      return { debut: addDays(today, -89), fin: today };
    case "6m":
      return { debut: addDays(addMonths(today, -6), 1), fin: today };
    case "1a":
      return { debut: addDays(addMonths(today, -12), 1), fin: today };
    case "tout":
      return { debut: null, fin: today };
    case "dates":
      if (!isIsoDate(f.from) || !isIsoDate(f.to) || f.from > f.to) return null;
      return { debut: f.from, fin: f.to };
  }
}

const shortDate = new Intl.DateTimeFormat("fr-FR", { timeZone: "UTC", day: "numeric", month: "short", year: "numeric" });

/** « 3 sept. 2026 ». */
export function formatDay(iso: string): string {
  return shortDate.format(new Date(`${iso}T12:00:00Z`));
}

/** Le nom de la période, pour le titre des gains. */
export function periodLabel(f: Pick<DashboardFilters, "period" | "from" | "to">): string {
  if (f.period === "dates") {
    return isIsoDate(f.from) && isIsoDate(f.to) ? `du ${formatDay(f.from)} au ${formatDay(f.to)}` : "dates précises";
  }
  const option = PERIOD_OPTIONS.find((o) => o.key === f.period);
  return option ? option.label : "30 derniers jours";
}

/** À quoi on compare les gains (la même durée juste avant). */
export function comparisonLabel(period: PeriodKey, days: number): string {
  if (period === "aujourdhui") return "par rapport à hier";
  if (period === "hier") return "par rapport à avant-hier";
  return days === 1 ? "par rapport à la veille" : `par rapport aux ${days} jours d'avant`;
}

/** Les filtres, dans l'adresse de /api/admin/dashboard. */
export function filtersToParams(f: DashboardFilters): URLSearchParams {
  const params = new URLSearchParams({ periode: f.period });
  if (f.period === "dates") {
    if (f.from) params.set("du", f.from);
    if (f.to) params.set("au", f.to);
  }
  if (f.creator !== null) params.set("createur", String(f.creator));
  if (f.net) params.set("net", "1");
  return params;
}

export function filtersFromParams(params: URLSearchParams): DashboardFilters {
  const period = PERIOD_OPTIONS.some((o) => o.key === params.get("periode")) ? (params.get("periode") as PeriodKey) : "30j";
  const creator = Number(params.get("createur"));
  return {
    period,
    from: params.get("du") ?? undefined,
    to: params.get("au") ?? undefined,
    creator: Number.isSafeInteger(creator) && creator > 0 ? creator : null,
    net: params.get("net") === "1",
  };
}

/** « Moins de 10 € », « 10 à 25 € », « 100 € et plus ». */
export function bucketLabel(minCents: number, maxCents: number | null): string {
  const e = (cents: number) => `${Math.round(cents / 100)} €`;
  if (minCents <= 0 && maxCents !== null) return `Moins de ${e(maxCents)}`;
  if (maxCents === null) return `${e(minCents)} et plus`;
  return `${Math.round(minCents / 100)} à ${e(maxCents)}`;
}

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
export function change(current: number, previous: number | null): number | null {
  if (previous === null || previous <= 0) return null;
  return Math.round(((current - previous) / previous) * 100);
}
