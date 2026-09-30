"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ALERT_TITLE, alertPath, alertSummary, type TeamAlert } from "@/lib/alerts";
import { OPEN_CONVERSATION } from "./messages/events";
import { alertDate, markAlertsSeen, useAlerts } from "./alerts-store";
import { setManual } from "./messages/actions";

// Le bandeau « flash » : dès qu'une nouvelle alerte arrive (contre-offre,
// urgence), il s'affiche en haut de chaque page de
// l'espace de l'équipe, avec « Prendre la main » en un clic. Fermé, il ne
// revient que pour une alerte plus récente.

export const ALERT_STYLE: Record<TeamAlert["kind"], string> = {
  urgence: "bg-bad text-white",
  contre_offre: "bg-accent text-white",
};

export function AlertFlash() {
  const { alerts, seenUntil } = useAlerts();
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (seenUntil === null) return null;
  const fresh = alerts.filter((a) => alertDate(a) > seenUntil);
  if (!fresh.length) return null;
  // La plus pressante des nouvelles : une urgence d'abord, sinon la plus récente.
  const alert = fresh.find((a) => a.kind === "urgence") ?? fresh[0];
  const others = fresh.length - 1;
  const href = alertPath(alert);

  async function takeOver() {
    setBusy(true);
    setError(null);
    const result = await setManual(alert.user_id, alert.creator_id, true);
    setBusy(false);
    if (!result.ok) return setError(result.error);
    markAlertsSeen();
    go();
  }

  /** Ouvre la conversation ; déjà dans l'onglet Messages, sans recharger la page. */
  function go(e?: React.MouseEvent) {
    markAlertsSeen();
    if (window.location.pathname === "/admin/messages") {
      e?.preventDefault();
      window.dispatchEvent(new CustomEvent(OPEN_CONVERSATION, { detail: `${alert.user_id}:${alert.creator_id}` }));
      return;
    }
    if (!e) router.push(href);
  }

  return (
    <div className="fixed inset-x-0 top-0 z-30 px-3 pt-[calc(0.5rem+env(safe-area-inset-top))]">
      <div
        role="alert"
        className={`mx-auto flex max-w-2xl flex-wrap items-center gap-x-3 gap-y-2 rounded-2xl px-4 py-3 shadow-lg ${ALERT_STYLE[alert.kind]}`}
      >
        <p className="min-w-0 flex-1 text-sm">
          <span className="font-bold">{ALERT_TITLE[alert.kind]}</span> · {alert.nom ?? "Une personne"} avec {alert.creatrice}
          <span className="block opacity-90">{alertSummary(alert)}</span>
          {others > 0 && (
            <span className="block text-xs opacity-80">
              et {others} autre{others > 1 ? "s" : ""} alerte{others > 1 ? "s" : ""}
            </span>
          )}
          {error && <span className="block text-xs font-semibold">{error}</span>}
        </p>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={takeOver}
            className="rounded-full bg-white px-3 py-1.5 text-sm font-bold text-black disabled:opacity-60"
          >
            Prendre la main
          </button>
          <Link
            href={href}
            onClick={go}
            className="rounded-full border border-current px-3 py-1.5 text-sm font-semibold"
          >
            Ouvrir
          </Link>
          <button
            type="button"
            onClick={markAlertsSeen}
            aria-label="Fermer l'alerte"
            className="flex size-8 items-center justify-center rounded-full text-lg leading-none hover:bg-white/15"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
}
