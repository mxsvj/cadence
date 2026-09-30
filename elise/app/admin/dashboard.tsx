"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState, useTransition } from "react";
import {
  NET_FEES,
  PERIOD_OPTIONS,
  addDays,
  change,
  comparisonLabel,
  describePurchase,
  filtersToParams,
  formatEuros,
  isIsoDate,
  parisToday,
  periodLabel,
  timeAgo,
  type DashboardData,
  type DashboardFilters,
  type PeriodKey,
} from "@/lib/dashboard";
import { clearDemo, fillDemo, simulatePurchase } from "./actions";
import { EarningsChart } from "./chart";
import { LtvChart } from "./ltv-chart";
import { OpenAlerts } from "./open-alerts";

/** Toutes les combien de secondes les chiffres sont redemandés. */
const REFRESH_MS = 4000;

type Filters = DashboardFilters;

const control = "rounded-full border border-line bg-surface px-3 py-1.5 text-sm";

export function Dashboard({ initial, initialFilters }: { initial: DashboardData; initialFilters: DashboardFilters }) {
  const [data, setData] = useState(initial);
  const [filters, setFilters] = useState<Filters>(initialFilters);
  // Les dates précises en cours de saisie (appliquées dès qu'elles sont valables).
  const [from, setFrom] = useState(initialFilters.from ?? initial.debut ?? "");
  const [to, setTo] = useState(initialFilters.to ?? initial.fin ?? "");
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
    const params = filtersToParams(f);
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
    // Les filtres restent dans l'adresse : recharger la page les garde.
    window.history.replaceState(null, "", `/admin?${filtersToParams(next)}`);
    void refresh(next);
  }

  function choosePeriod(period: PeriodKey) {
    if (period !== "dates") return applyFilters({ ...filters, period, from: undefined, to: undefined });
    // Dates précises : on part de la période affichée, modifiable au calendrier.
    const today = parisToday();
    const start = isIsoDate(data.debut) ? data.debut : addDays(today, -6);
    const end = isIsoDate(data.fin) ? data.fin : today;
    setFrom(start);
    setTo(end);
    applyFilters({ ...filters, period, from: start, to: end });
  }

  function chooseDates(nextFrom: string, nextTo: string) {
    setFrom(nextFrom);
    setTo(nextTo);
    if (isIsoDate(nextFrom) && isIsoDate(nextTo) && nextFrom <= nextTo) {
      applyFilters({ ...filters, period: "dates", from: nextFrom, to: nextTo });
    }
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
  const creators = data.createurs ?? [];
  const creatorName = creators.find((c) => c.id === filters.creator)?.nom ?? null;
  const secondsAgo = Math.max(0, Math.round((now - updatedAt) / 1000));
  const datesInvalid = filters.period === "dates" && (!isIsoDate(from) || !isIsoDate(to) || from > to);
  const heading = [periodLabel(filters), creatorName, filters.net ? "net" : null].filter(Boolean).join(" · ");

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-serif text-3xl">Tableau de bord</h1>
          <p className="text-sm text-muted">Les gains, en direct</p>
        </div>
        <div className="flex items-center gap-4">
          <p className="flex items-center gap-2 text-sm" role="status" suppressHydrationWarning>
            <span className="relative flex size-2.5">
              {!offline && <span className="absolute inline-flex size-full animate-ping rounded-full bg-good opacity-60" />}
              <span className={`relative inline-flex size-2.5 rounded-full ${offline ? "bg-muted" : "bg-good"}`} />
            </span>
            {offline ? "Hors ligne, nouvel essai…" : `En direct · mis à jour il y a ${secondsAgo} s`}
          </p>
        </div>
      </header>

      <OpenAlerts now={now} />

      {data.demo && (
        <p className="rounded-2xl border border-line bg-accent-soft px-4 py-3 text-sm">
          <strong>Données de démonstration.</strong> Aucun paiement n&apos;est encore branché : les achats marqués
          « démo » sont fictifs. Ils s&apos;effacent en bas de page.
        </p>
      )}

      {/* Les filtres : ils valent pour tout ce qui suit. */}
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={filters.period}
            onChange={(e) => choosePeriod(e.target.value as PeriodKey)}
            aria-label="Période"
            className={control}
          >
            {PERIOD_OPTIONS.map((o) => (
              <option key={o.key} value={o.key}>
                {o.label}
              </option>
            ))}
          </select>
          {filters.period === "dates" && (
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <label className="flex items-center gap-1.5">
                <span className="text-muted">Du</span>
                <input
                  type="date"
                  value={from}
                  max={to || undefined}
                  onChange={(e) => chooseDates(e.target.value, to)}
                  className={control}
                />
              </label>
              <label className="flex items-center gap-1.5">
                <span className="text-muted">au</span>
                <input
                  type="date"
                  value={to}
                  min={from || undefined}
                  max={parisToday()}
                  onChange={(e) => chooseDates(from, e.target.value)}
                  className={control}
                />
              </label>
            </div>
          )}
          <div role="group" aria-label="Montants" className="flex rounded-full border border-line bg-surface p-1">
            {([false, true] as const).map((net) => (
              <button
                key={String(net)}
                type="button"
                aria-pressed={filters.net === net}
                disabled={data.outdated}
                onClick={() => applyFilters({ ...filters, net })}
                className={`rounded-full px-3 py-1 text-sm font-semibold disabled:opacity-50 ${
                  filters.net === net ? "bg-accent text-white" : "text-muted hover:text-foreground"
                }`}
              >
                {net ? "Net" : "Brut"}
              </button>
            ))}
          </div>
          <select
            value={filters.creator ?? ""}
            onChange={(e) => applyFilters({ ...filters, creator: e.target.value ? Number(e.target.value) : null })}
            aria-label="Créatrice"
            disabled={data.outdated}
            className={`${control} max-w-64 disabled:opacity-50`}
          >
            <option value="">Toutes les créatrices</option>
            {creators.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nom}
              </option>
            ))}
          </select>
        </div>
        {datesInvalid && <p className="text-sm text-bad">Choisissez une date de début avant la date de fin.</p>}
        {filters.net && !data.outdated && (
          <p className="text-xs text-muted">Net : après les frais de paiement estimés, {NET_FEES}.</p>
        )}
        {data.outdated && (
          <p className="text-sm text-muted">
            Les filtres Net et Créatrice arrivent quand la base est à jour : relancez supabase/schema.sql dans Supabase.
          </p>
        )}
      </div>

      {/* Les chiffres clés */}
      <section
        aria-label="Chiffres clés"
        className="grid grid-cols-1 gap-4 transition-opacity sm:grid-cols-2 lg:grid-cols-4"
        style={{ opacity: dimmed ? 0.45 : 1 }}
      >
        <div className="flex flex-col justify-center gap-1 rounded-3xl border border-line bg-surface p-5 sm:col-span-2 lg:row-span-2">
          <p className="text-sm text-muted first-letter:uppercase">Gains · {heading}</p>
          <p className="text-5xl font-bold tracking-tight">{formatEuros(t.periode)}</p>
          <p className="text-sm">
            {filters.period === "tout" ? (
              <span className="text-muted">Depuis le premier achat</span>
            ) : delta === null ? (
              <span className="text-muted">Rien à comparer sur la période précédente</span>
            ) : (
              <>
                <span className={`font-bold ${delta >= 0 ? "text-good" : "text-bad"}`}>
                  {delta >= 0 ? "▲" : "▼"} {delta >= 0 ? "+" : "−"}
                  {Math.abs(delta)} %
                </span>{" "}
                <span className="text-muted">{comparisonLabel(filters.period, data.jours)}</span>
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
          label="Contenus vendus"
          value={formatEuros(t.contenus.cents)}
          detail={plural(t.contenus.nombre, "contenu débloqué", "contenus débloqués")}
        />
        <Tile
          label="Abonnements actifs"
          value={t.abonnements.actifs.toLocaleString("fr-FR")}
          detail={`${formatEuros(t.abonnements.cents)} encaissés sur la période`}
        />
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="min-w-0 rounded-3xl border border-line bg-surface p-5 lg:col-span-2">
          <EarningsChart
            serie={data.serie}
            pas={data.pas ?? "jour"}
            endsToday={(data.fin ?? parisToday()) === parisToday()}
            dimmed={dimmed}
          />
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
              <p>
                {describePurchase(latest)}
                {latest.createur ? <span className="text-muted"> · {latest.createur}</span> : null}
              </p>
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

      {/* La LTV : ce qu'un client rapporte sur toute sa vie */}
      <section
        aria-label="LTV"
        className="grid grid-cols-1 gap-6 rounded-3xl border border-line bg-surface p-5 transition-opacity lg:grid-cols-2"
        style={{ opacity: dimmed ? 0.45 : 1 }}
      >
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="font-bold">LTV</h2>
            <p className="text-sm text-muted">
              Ce qu&apos;un client a dépensé au total, depuis son premier achat (tout l&apos;historique
              {creatorName ? `, avec ${creatorName}` : ""}
              {filters.net ? ", net" : ""}).
            </p>
          </div>
          <p className="text-5xl font-bold tracking-tight">{formatEuros(data.ltv.moyenne_cents)}</p>
          <p className="-mt-3 text-sm text-muted">en moyenne par client</p>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-3">
            <Figure label="LTV médiane" value={formatEuros(data.ltv.mediane_cents)} />
            <Figure label="Meilleure LTV" value={formatEuros(data.ltv.max_cents)} />
            <Figure label="Clients" value={data.ltv.clients.toLocaleString("fr-FR")} />
            <Figure label="Panier moyen" value={formatEuros(data.ltv.panier_moyen_cents)} />
            <Figure
              label="Achats par client"
              value={Number(data.ltv.achats_par_client).toLocaleString("fr-FR", { maximumFractionDigits: 1 })}
            />
            <Figure label="Durée de vie moyenne" value={plural(data.ltv.duree_moyenne_jours, "jour")} />
          </dl>
        </div>
        <LtvChart buckets={data.repartition ?? []} />
      </section>

      {/* Par personne */}
      <section className="flex min-w-0 flex-col gap-3 rounded-3xl border border-line bg-surface p-5">
        <div>
          <h2 className="font-bold">Par personne</h2>
          <p className="text-sm text-muted">
            Depuis le début{creatorName ? `, avec ${creatorName}` : ""}{filters.net ? ", net" : ""}.
          </p>
        </div>
        {data.clients.length === 0 ? (
          <p className="text-muted">Personne n&apos;a encore rien acheté.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="text-left text-xs uppercase tracking-wide text-muted">
                <tr className="border-b border-line">
                  <th className="py-2 pr-3 font-bold">Personne</th>
                  <th className="py-2 pr-3 text-right font-bold">Pourboires</th>
                  <th className="py-2 pr-3 text-right font-bold">Messages achetés</th>
                  <th className="py-2 pr-3 text-right font-bold">Contenus</th>
                  <th className="py-2 pr-3 font-bold">Abonnement</th>
                  <th className="py-2 pr-3 text-right font-bold">LTV</th>
                  <th className="py-2 text-right font-bold">Dernier achat</th>
                </tr>
              </thead>
              <tbody className="tabular-nums">
                {data.clients.map((c) => (
                  <tr key={c.client} className="border-b border-line last:border-0">
                    <td className="py-2 pr-3">
                      <span className="font-semibold">{c.nom}</span>
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
                    <td className="py-2 pr-3 text-right">
                      {formatEuros(c.contenus_cents)}
                      <span className="block text-xs text-muted">{plural(c.contenus_nombre, "contenu")}</span>
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

function plural(n: number, word: string, many = `${word}s`): string {
  return `${Number(n).toLocaleString("fr-FR")} ${n > 1 ? many : word}`;
}

function Figure({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="text-xl font-bold tracking-tight">{value}</dd>
    </div>
  );
}
