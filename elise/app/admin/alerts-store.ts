"use client";

import { useSyncExternalStore } from "react";
import type { TeamAlert } from "@/lib/alerts";

// Les alertes à traiter, redemandées au serveur toutes les quelques secondes
// tant qu'une partie de l'espace de l'équipe les affiche (bandeau flash,
// pastille de l'onglet Messages, liste du tableau de bord). Une seule
// demande pour tous : ils partagent ce magasin.

type State = {
  alerts: TeamAlert[];
  outdated: boolean;
  loaded: boolean;
  /** Date de la dernière alerte déjà montrée dans le bandeau, sur cet appareil ("" : aucune ; null : pas encore lu). */
  seenUntil: string | null;
};

const POLL_MS = 8000;
/** Onglet en arrière-plan : on redemande moins souvent. */
const HIDDEN_POLL_MS = 30_000;
const EMPTY: State = { alerts: [], outdated: false, loaded: false, seenUntil: null };
const SEEN_KEY = "elise-alertes-vues";

let state: State = EMPTY;
const listeners = new Set<() => void>();
let timer: number | null = null;
let lastFetch = 0;

function emit() {
  for (const listener of listeners) listener();
}

export async function refreshAlerts(): Promise<void> {
  lastFetch = Date.now();
  const res = await fetch("/api/admin/alertes", { cache: "no-store" }).catch(() => null);
  if (!res?.ok) return;
  const data = (await res.json().catch(() => null)) as { alerts: TeamAlert[]; outdated: boolean } | null;
  if (!data) return;
  const same =
    state.loaded &&
    state.outdated === data.outdated &&
    JSON.stringify(state.alerts) === JSON.stringify(data.alerts);
  if (same) return;
  state = { ...state, alerts: data.alerts, outdated: data.outdated, loaded: true };
  emit();
}

function tick() {
  const wait = document.visibilityState === "visible" ? POLL_MS : HIDDEN_POLL_MS;
  if (Date.now() - lastFetch >= wait - 500) void refreshAlerts();
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  if (state.seenUntil === null) {
    let seen = "";
    try {
      seen = window.localStorage.getItem(SEEN_KEY) ?? "";
    } catch {
      // Stockage bloqué (navigation privée…) : le bandeau montre tout.
    }
    state = { ...state, seenUntil: seen };
  }
  if (timer === null) {
    void refreshAlerts();
    timer = window.setInterval(tick, POLL_MS);
  }
  return () => {
    listeners.delete(listener);
    if (!listeners.size && timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
  };
}

/** Les alertes à traiter, les plus récentes d'abord. */
export function useAlerts(): State {
  return useSyncExternalStore(
    subscribe,
    () => state,
    () => EMPTY,
  );
}

/** La date d'une alerte (créée, ou mise à jour par une nouvelle contre-offre). */
export const alertDate = (a: TeamAlert) => a.date ?? a.created_at ?? "";

/** Le bandeau a été vu ou fermé : les alertes présentes ne s'y afficheront plus. */
export function markAlertsSeen(): void {
  const latest = state.alerts.reduce((max, a) => (alertDate(a) > max ? alertDate(a) : max), state.seenUntil ?? "");
  if (latest === state.seenUntil) return;
  try {
    window.localStorage.setItem(SEEN_KEY, latest);
  } catch {
    // Tant pis : le bandeau se refermera, sans s'en souvenir.
  }
  state = { ...state, seenUntil: latest };
  emit();
}

/** Retire tout de suite une alerte traitée, sans attendre le prochain passage. */
export function dropAlerts(match: (a: TeamAlert) => boolean): void {
  const alerts = state.alerts.filter((a) => !match(a));
  if (alerts.length === state.alerts.length) return;
  state = { ...state, alerts };
  emit();
}
