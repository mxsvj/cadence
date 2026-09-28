"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState, useTransition } from "react";
import {
  PERIODS,
  change,
  describePurchase,
  formatEuros,
  timeAgo,
  type DashboardData,
} from "@/lib/dashboard";
import { clearDemo, fillDemo, simulatePurchase } from "./actions";
import { EarningsChart } from "./chart";

/** Toutes les combien de secondes les chiffres sont redemandés. */
const REFRESH_MS = 4000;

type Filters = { period: number; client: string | null };

export function Dashboard({ initial }: { initial: DashboardData }) {
  const [data, setData] = useState(initial);
  const [filters, setFilters] = useState<Filters>({ period: initial.jours, client: null });
  const [dimmed, setDimmed] = useState(false);
  const [offline, setOffline] = useState(false);
  const [updatedAt, setUpdatedAt] = useState(() => Date.parse(initial.genere_le));
  const [now, setNow] = useState(() => Date.parse(initial.genere_le));
  const [flashId, setFlashId] = useState<number | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirmClear, setConfirmClear] = useState(false);
  const [busy, startBusy] = useTransition();
  const router = useRouter();

  const filtersRef = useRef(filters);
  const topId = useRef<number | null>(initial.derniers[0]?.id ?? null);
  const requestId = useRef(0);

  const refresh = useCallback(async (next?: Filters) => {
    const f = next ?? filtersRef.current;
    const id = ++requestId.current;
    const params = new URLSearchParams({ jours: String(f.period) });
    if (f.client) params.set("client", f.client);
    try {
      const res = await fetch(`/api/admin/dashboard?${params}`, { cache: "no-store" });
      if (res.status === 401 || res.status === 404) {
        router.replace("/"); // session expirée ou droits retirés
        return;
      }
      if (!res.ok) throw new Error(String(res.status));
      const fresh = (await res.json()) as DashboardData;
      if (id !== requestId.current) return; // une réponse plus récente est déjà là
      const newTop = fresh.derniers[0]?.id ?? null;
      // Un nouvel achat est arrivé depuis le dernier passage : on le fait briller.
      if (!next && newTop !== null && topId.current !== null && newTop > topId.current) {
        setFlashId(newTop);
        window.setTimeout(() => setFlashId((current) => (current === newTop ? null : current)), 2500);
      }
      topId.current = newTop;
      setData(fresh);
      setUpdatedAt(Date.now());
      setOffline(false);
    } catch {
      if (id === requestId.current) setOffline(true);
    } finally {
      if (id === requestId.current) setDimmed(false);
    }
  }, [router]);

  // Le direct : on redemande les chiffres régulièrement, onglet visible.
  useEffect(() => {
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") void refresh();
    }, REFRESH_MS);
    const tick = window.setInterval(() => setNow(Date.now()), 1000);
    return () => {
      window.clearInterval(timer);
      window.clearInterval(tick);
    };
  }, [refresh]);

  function applyFilters(next: Filters) {
    filtersRef.current = next;
    setFilters(next);
    setDimmed(true); // l'ancien rendu reste visible, atténué, le temps du rechargement
    void refresh(next);
  }

  function demo(action: () => Promise<{ error?: string }>, done: string) {
    startBusy(async () => {
      const result = await action();
      setNotice(result.error ?? done);
      setConfirmClear(false);
      await refresh();
    });
  }

  const t = data.totaux;
  const delta = change(t.periode, t.periode_precedente);
  const latest = data.derniers[0] ?? null;
  const selected = data.clients.find((c) => c.client === filters.client) ?? null;
  const secondsAgo = Math.max(0, Math.round((now - updatedAt) / 1000));

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-serif text-3xl">Tableau de bord</h1>
          <p className="text-sm text-muted">Les gains d&apos;Élise</p>
        </div>
        <div className="flex items-center gap-4">
          <p className="flex items-center gap-2 text-sm" role="status" suppressHydrationWarning>
            <span className="relative flex size-2.5">
              {!offline && <span className="absolute inline-flex size-full animate-ping rounded-full bg-good opacity-60" />}
              <span className={`relative inline-flex size-2.5 rounded-full ${offline ? "bg-muted" : "bg-good"}`} />
            </span>
            {offline ? "Hors ligne, nouvel essai…" : `En direct · mis à jour il y a ${secondsAgo} s`}
          </p>
          <Link href="/" className="text-sm text-muted underline underline-offset-4">
            Conversation
          </Link>
        </div>
      </header>

      {data.demo && (
        <p className="rounded-2xl border border-line bg-accent-soft px-4 py-3 text-sm">
          <strong>Données de démonstration.</strong> Aucun paiement n&apos;est encore branché : les achats marqués
          « démo » sont fictifs. Ils s&apos;effacent en bas de page.
        </p>
      )}

      {/* Les filtres : ils valent pour tout ce qui suit. */}
      <div className="flex flex-wrap items-center gap-3">
        <div role="group" aria-label="Période" className="flex rounded-full border border-line bg-surface p-1">
          {PERIODS.map((p) => (
            <button
              key={p}
              type="button"
              aria-pressed={filters.period === p}
              onClick={() => applyFilters({ ...filters, period: p })}
              className={`rounded-full px-3 py-1 text-sm font-semibold ${
                filters.period === p ? "bg-accent text-white" : "text-muted hover:text-foreground"
              }`}
            >
              {p} jours
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2 text-sm">
          <span className="text-muted">Personne</span>
          <select
            id="filtre-personne"
            value={filters.client ?? ""}
            onChange={(e) => applyFilters({ ...filters, client: e.target.value || null })}
            className="max-w-64 rounded-full border border-line bg-surface px-3 py-1.5"
          >
            <option value="">Toutes les personnes</option>
            {data.clients.map((c) => (
              <option key={c.client} value={c.client}>
                {c.nom}
                {c.demo ? " (démo)" : ""}
              </option>
            ))}
          </select>
        </label>
        {filters.client && (
          <button
            type="button"
            onClick={() => applyFilters({ ...filters, client: null })}
            className="text-sm text-muted underline underline-offset-4"
          >
            Voir tout le monde
          </button>
        )}
      </div>

      {/* Les chiffres clés */}
      <section
        aria-label="Chiffres clés"
        className="grid grid-cols-1 gap-4 transition-opacity sm:grid-cols-2 lg:grid-cols-4"
        style={{ opacity: dimmed ? 0.45 : 1 }}
      >
        <div className="flex flex-col gap-1 rounded-3xl border border-line bg-surface p-5 sm:col-span-2 lg:col-span-1 lg:row-span-1">
          <p className="text-sm text-muted">
            Gains · {filters.period} derniers jours{selected ? ` · ${selected.nom}` : ""}
          </p>
          <p className="text-5xl font-bold tracking-tight">{formatEuros(t.periode)}</p>
          <p className="text-sm">
            {delta === null ? (
              <span className="text-muted">Rien à comparer sur la période précédente</span>
            ) : (
              <>
                <span className={`font-bold ${delta >= 0 ? "text-good" : "text-bad"}`}>
                  {delta >= 0 ? "▲" : "▼"} {delta >= 0 ? "+" : "−"}
                  {Math.abs(delta)} %
                </span>{" "}
                <span className="text-muted">par rapport aux {filters.period} jours d&apos;avant</span>
              </>
            )}
          </p>
          <p className="text-sm text-muted">Depuis le début : {formatEuros(t.depuis_le_debut)}</p>
        </div>
        <Tile label="Pourboires" value={formatEuros(t.pourboires.cents)} detail={plural(t.pourboires.nombre, "pourboire")} />
        <Tile
          label="Messages achetés"
          value={t.messages.nombre.toLocaleString("fr-FR")}
          detail={`${plural(t.messages.achats, "achat")} · ${formatEuros(t.messages.cents)}`}
        />
        <Tile
          label="Abonnements actifs"
          value={t.abonnements.actifs.toLocaleString("fr-FR")}
          detail={`${formatEuros(t.abonnements.cents)} encaissés sur la période`}
        />
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="min-w-0 rounded-3xl border border-line bg-surface p-5 lg:col-span-2">
          <EarningsChart serie={data.serie} dimmed={dimmed} />
        </section>

        {/* Le dernier achat, en direct */}
        <section aria-live="polite" className="flex min-w-0 flex-col gap-4 rounded-3xl border border-line bg-surface p-5">
          <h2 className="font-bold">Dernier achat</h2>
          {latest ? (
            <div
              key={latest.id}
              className={`rounded-2xl p-4 transition-colors ${flashId === latest.id ? "animate-pulse bg-accent-soft" : "bg-background"}`}
            >
              <p className="font-bold break-words">{latest.nom}</p>
              <p>{describePurchase(latest)}</p>
              <p className="text-sm text-muted" suppressHydrationWarning>
                {timeAgo(latest.date, now)}
                {latest.demo ? " · démo" : ""}
              </p>
            </div>
          ) : (
            <p className="text-muted">Aucun achat pour l&apos;instant.</p>
          )}
          {data.derniers.length > 1 && (
            <>
              <h3 className="text-sm font-bold text-muted">Juste avant</h3>
              <ul className="flex flex-col divide-y divide-line text-sm">
                {data.derniers.slice(1, 6).map((p) => (
                  <li key={p.id} className="flex items-baseline justify-between gap-3 py-2">
                    <span className="min-w-0">
                      <span className="block truncate font-semibold">{p.nom}</span>
                      <span className="text-muted">{describePurchase(p)}</span>
                    </span>
                    <span className="shrink-0 text-muted" suppressHydrationWarning>
                      {timeAgo(p.date, now)}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      </div>

      {/* Par personne */}
      <section className="flex min-w-0 flex-col gap-3 rounded-3xl border border-line bg-surface p-5">
        <div>
          <h2 className="font-bold">Par personne</h2>
          <p className="text-sm text-muted">Depuis le début. Touchez un nom pour ne voir que cette personne.</p>
        </div>
        {data.clients.length === 0 ? (
          <p className="text-muted">Personne n&apos;a encore rien acheté.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="text-left text-xs uppercase tracking-wide text-muted">
                <tr className="border-b border-line">
                  <th className="py-2 pr-3 font-bold">Personne</th>
                  <th className="py-2 pr-3 text-right font-bold">Pourboires</th>
                  <th className="py-2 pr-3 text-right font-bold">Messages achetés</th>
                  <th className="py-2 pr-3 font-bold">Abonnement</th>
                  <th className="py-2 pr-3 text-right font-bold">Total</th>
                  <th className="py-2 text-right font-bold">Dernier achat</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                {data.clients.map((c) => (
                  <tr key={c.client} className={`border-b border-line last:border-0 ${c.client === filters.client ? "bg-accent-soft" : ""}`}>
                    <td className="py-2 pr-3">
                      <button
                        type="button"
                        onClick={() => applyFilters({ ...filters, client: c.client })}
                        className="text-left font-semibold underline-offset-4 hover:underline"
                      >
                        {c.nom}
                      </button>
                      {c.demo && <span className="ml-2 text-xs text-muted">démo</span>}
                    </td>
                    <td className="py-2 pr-3 text-right">
                      {formatEuros(c.pourboires_cents)}
                      <span className="block text-xs text-muted">{plural(c.pourboires_nombre, "pourboire")}</span>
                    </td>
                    <td className="py-2 pr-3 text-right">
                      {c.messages_nombre.toLocaleString("fr-FR")}
                      <span className="block text-xs text-muted">{formatEuros(c.messages_cents)}</span>
                    </td>
                    <td className="py-2 pr-3">
                      {c.abonne ? (
                        <span className="font-semibold text-good">✓ Actif</span>
                      ) : (
                        <span className="text-muted">Non</span>
                      )}
                    </td>
                    <td className="py-2 pr-3 text-right font-bold">{formatEuros(c.total_cents)}</td>
                    <td className="py-2 text-right text-muted whitespace-nowrap" suppressHydrationWarning>
                      {timeAgo(c.dernier_achat, now)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* La démonstration */}
      <section className="flex flex-col gap-3 rounded-3xl border border-dashed border-line p-5">
        <div>
          <h2 className="font-bold">Démonstration</h2>
          <p className="text-sm text-muted">
            Aucun paiement n&apos;est encore branché. Ces boutons créent des achats fictifs, marqués « démo », pour voir
            le tableau de bord vivre. Les vrais achats n&apos;y sont jamais mélangés.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={() => demo(simulatePurchase, "Achat fictif ajouté.")}
            className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-60"
          >
            Simuler un achat
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => demo(fillDemo, "60 jours d'achats fictifs ajoutés.")}
            className="rounded-full border border-line px-4 py-2 text-sm font-semibold disabled:opacity-60"
          >
            Remplir 60 jours de démo
          </button>
          {data.demo &&
            (confirmClear ? (
              <button
                type="button"
                disabled={busy}
                onClick={() => demo(clearDemo, "Achats fictifs effacés.")}
                className="rounded-full border border-bad px-4 py-2 text-sm font-bold text-bad disabled:opacity-60"
              >
                Confirmer : effacer la démo
              </button>
            ) : (
              <button
                type="button"
                disabled={busy}
                onClick={() => setConfirmClear(true)}
                className="rounded-full border border-line px-4 py-2 text-sm font-semibold text-muted disabled:opacity-60"
              >
                Effacer la démo
              </button>
            ))}
        </div>
        {notice && (
          <p role="status" className="text-sm text-muted">
            {notice}
          </p>
        )}
      </section>
    </div>
  );
}

function Tile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-3xl border border-line bg-surface p-5">
      <p className="text-sm text-muted">{label}</p>
      <p className="text-3xl font-bold tracking-tight">{value}</p>
      <p className="text-sm text-muted">{detail}</p>
    </div>
  );
}

function plural(n: number, word: string): string {
  return `${n.toLocaleString("fr-FR")} ${word}${n > 1 ? "s" : ""}`;
}
