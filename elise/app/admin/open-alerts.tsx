"use client";

import Link from "next/link";
import { useState } from "react";
import { ALERT_TITLE, alertPath, alertSummary } from "@/lib/alerts";
import { timeAgo } from "@/lib/dashboard";
import { ALERT_STYLE } from "./alert-flash";
import { alertDate, dropAlerts, useAlerts } from "./alerts-store";
import { handleAlerts, setManual } from "./messages/actions";

// Sur le tableau de bord : les alertes à traiter, avec les mêmes gestes que
// dans la messagerie (ouvrir, prendre la main, marquer traité).
export function OpenAlerts({ now }: { now: number }) {
  const { alerts, outdated, loaded } = useAlerts();
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  if (!loaded) return null;
  if (outdated) {
    return (
      <p className="rounded-2xl border border-line bg-accent-soft px-4 py-3 text-sm">
        Les alertes de l&apos;équipe ne sont pas encore actives : relancez supabase/schema.sql dans Supabase.
      </p>
    );
  }
  if (!alerts.length) return null;

  async function act(action: () => Promise<{ ok: boolean; error?: string }>, done: string) {
    setBusy(true);
    const result = await action();
    setBusy(false);
    setNotice(result.ok ? done : (result.error ?? "L'action n'a pas abouti."));
  }

  return (
    <section aria-labelledby="titre-alertes" className="flex flex-col gap-2 rounded-3xl border border-line bg-surface p-4">
      <h2 id="titre-alertes" className="font-bold">
        À traiter <span className="font-normal text-muted">· {alerts.length}</span>
      </h2>
      <ul className="flex flex-col gap-2">
        {alerts.slice(0, 8).map((a) => (
          <li key={a.id} className="flex flex-wrap items-center gap-2 text-sm">
            <span className={`shrink-0 rounded px-1.5 text-xs font-semibold ${ALERT_STYLE[a.kind]}`}>{ALERT_TITLE[a.kind]}</span>
            <span className="min-w-0 flex-1">
              <span className="font-semibold">{a.nom ?? "Une personne"}</span>
              <span className="text-muted"> avec {a.creatrice}</span> · {alertSummary(a)}
              <span className="text-muted" suppressHydrationWarning>
                {" "}
                · {timeAgo(alertDate(a), now)}
              </span>
            </span>
            <span className="flex shrink-0 gap-2">
              <Link href={alertPath(a)} className="rounded-full border border-line px-3 py-1 text-xs font-semibold">
                Ouvrir
              </Link>
              <button
                type="button"
                disabled={busy}
                onClick={() => act(() => setManual(a.user_id, a.creator_id, true), `Vous avez la main avec ${a.nom ?? "cette personne"}.`)}
                className="rounded-full bg-accent px-3 py-1 text-xs font-bold text-white disabled:opacity-60"
              >
                Prendre la main
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() =>
                  act(async () => {
                    const result = await handleAlerts(a.user_id, a.creator_id, a.id);
                    if (result.ok) dropAlerts((x) => x.id === a.id);
                    return result;
                  }, "Alerte marquée traitée.")
                }
                className="rounded-full px-2 py-1 text-xs text-muted underline"
              >
                Traité
              </button>
            </span>
          </li>
        ))}
      </ul>
      {alerts.length > 8 && (
        <Link href="/admin/messages" className="text-sm text-muted underline">
          Voir les {alerts.length} alertes dans Messages
        </Link>
      )}
      {notice && (
        <p role="status" className="text-sm text-muted">
          {notice}
        </p>
      )}
    </section>
  );
}
