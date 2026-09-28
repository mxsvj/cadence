"use client";

import { useEffect, useRef, useState } from "react";
import { formatEuros, formatEurosRound, type DashboardData } from "@/lib/dashboard";

type Point = DashboardData["serie"][number];

/** Hauteur du tracé : plus haut sur grand écran. */
const plotHeight = (width: number) => (width >= 560 ? 320 : 220);
const AXIS_BAND = 28; // étiquettes de dates, sous le tracé
const PAD = { top: 14, right: 64, left: 56 }; // à droite : la place de l'étiquette finale

const dayShort = new Intl.DateTimeFormat("fr-FR", { timeZone: "UTC", day: "numeric", month: "short" });
const dayLong = new Intl.DateTimeFormat("fr-FR", { timeZone: "UTC", weekday: "long", day: "numeric", month: "long" });
const asDate = (jour: string) => new Date(`${jour}T12:00:00Z`);

/** Un pas d'axe « rond » (1, 2, 2,5 ou 5 × 10ⁿ) pour environ `count` graduations. */
function niceStep(max: number, count = 4): number {
  const raw = max / count;
  const power = 10 ** Math.floor(Math.log10(raw));
  const n = raw / power;
  return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * power;
}

/**
 * Courbe lissée qui passe par chaque point sans jamais les dépasser
 * (interpolation monotone de Fritsch-Carlson) : pas de bosse inventée,
 * pas de creux sous zéro.
 */
function smoothPath(pts: [number, number][]): string {
  const n = pts.length;
  if (n === 0) return "";
  if (n === 1) return `M${pts[0][0]},${pts[0][1]}`;
  const dx: number[] = [];
  const slope: number[] = [];
  for (let i = 0; i < n - 1; i++) {
    dx.push(pts[i + 1][0] - pts[i][0]);
    slope.push((pts[i + 1][1] - pts[i][1]) / dx[i]);
  }
  const t: number[] = [slope[0]];
  for (let i = 1; i < n - 1; i++) t.push(slope[i - 1] * slope[i] <= 0 ? 0 : (slope[i - 1] + slope[i]) / 2);
  t.push(slope[n - 2]);
  for (let i = 0; i < n - 1; i++) {
    if (slope[i] === 0) {
      t[i] = 0;
      t[i + 1] = 0;
      continue;
    }
    const a = t[i] / slope[i];
    const b = t[i + 1] / slope[i];
    const s = a * a + b * b;
    if (s > 9) {
      const k = 3 / Math.sqrt(s);
      t[i] = k * a * slope[i];
      t[i + 1] = k * b * slope[i];
    }
  }
  let d = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 0; i < n - 1; i++) {
    const [x0, y0] = pts[i];
    const [x1, y1] = pts[i + 1];
    const h = dx[i] / 3;
    d += ` C${x0 + h},${y0 + t[i] * h} ${x1 - h},${y1 - t[i + 1] * h} ${x1},${y1}`;
  }
  return d;
}

export function EarningsChart({ serie, dimmed }: { serie: Point[]; dimmed: boolean }) {
  const boxRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [active, setActive] = useState<number | null>(null);
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.round(entry.contentRect.width)));
    observer.observe(el);
    return () => observer.disconnect();
  }, [showTable]); // le cadre est recréé quand on revient du tableau

  const plotH = plotHeight(width);
  const n = serie.length;
  const max = Math.max(0, ...serie.map((p) => p.total));
  const step = niceStep(max > 0 ? max : 1000);
  const top = Math.max(step, Math.ceil(max / step) * step);
  const ticks = Array.from({ length: Math.round(top / step) + 1 }, (_, i) => i * step);

  const plotW = Math.max(0, width - PAD.left - PAD.right);
  const x = (i: number) => PAD.left + (n <= 1 ? plotW : (i / (n - 1)) * plotW);
  const y = (cents: number) => PAD.top + plotH - (cents / top) * plotH;
  const pts: [number, number][] = serie.map((p, i) => [x(i), y(p.total)]);
  const line = smoothPath(pts);
  const baseline = y(0);
  const area = n ? `${line} L${x(n - 1)},${baseline} L${x(0)},${baseline} Z` : "";

  const last = n - 1;

  // Des dates sous l'axe, en partant d'aujourd'hui, assez espacées pour ne
  // jamais se chevaucher (et pas collées à « Aujourd'hui », plus large).
  const fits = Math.max(2, Math.floor(plotW / 72));
  const every = Math.max(1, Math.ceil(n / fits));
  const dateTicks = serie
    .map((_, i) => i)
    .filter((i) => (last - i) % every === 0 && (i === last || x(last) - x(i) >= 96));
  const shown = active ?? null;
  const total = serie.reduce((s, p) => s + p.total, 0);

  function pick(clientX: number, target: Element) {
    const left = target.getBoundingClientRect().left;
    const ratio = plotW > 0 ? (clientX - left - PAD.left) / plotW : 1;
    setActive(Math.min(last, Math.max(0, Math.round(ratio * (n - 1)))));
  }

  function onKey(e: React.KeyboardEvent) {
    if (e.key === "ArrowLeft") setActive((a) => Math.max(0, (a ?? last) - 1));
    else if (e.key === "ArrowRight") setActive((a) => Math.min(last, (a ?? last) + 1));
    else if (e.key === "Escape") setActive(null);
    else return;
    e.preventDefault();
  }

  // L'infobulle se met à droite du repère, sinon à gauche, sinon au mieux
  // dans la largeur ; en haut du tracé, ou en bas si le point est haut.
  const tip = shown !== null ? serie[shown] : null;
  const TIP_W = 192;
  let tipLeft = 0;
  let tipLow = false;
  if (tip && shown !== null) {
    const px = x(shown);
    tipLeft = px + 12;
    if (tipLeft + TIP_W > width) tipLeft = px - 12 - TIP_W;
    if (tipLeft < 0) tipLeft = Math.max(0, Math.min(width - TIP_W, px - TIP_W / 2));
    tipLow = y(tip.total) < PAD.top + plotH / 2;
  }

  return (
    <figure className="flex min-w-0 flex-col gap-3">
      <figcaption className="flex items-baseline justify-between gap-3">
        <span>
          <span className="block font-bold">Gains par jour</span>
          <span className="text-sm text-muted">
            {n} derniers jours · {formatEuros(total)} au total
          </span>
        </span>
        <button
          type="button"
          onClick={() => setShowTable((s) => !s)}
          className="shrink-0 rounded-full border border-line px-3 py-1 text-sm hover:bg-accent-soft"
          aria-pressed={showTable}
        >
          {showTable ? "Voir la courbe" : "Voir le tableau"}
        </button>
      </figcaption>

      {showTable ? (
        <div className="max-h-80 overflow-auto rounded-xl border border-line">
          <table className="w-full text-sm tabular-nums">
            <thead className="sticky top-0 bg-surface text-left text-xs uppercase tracking-wide text-muted">
              <tr>
                <th className="px-3 py-2 font-bold">Jour</th>
                <th className="px-3 py-2 text-right font-bold">Total</th>
                <th className="px-3 py-2 text-right font-bold">Pourboires</th>
                <th className="px-3 py-2 text-right font-bold">Messages</th>
                <th className="px-3 py-2 text-right font-bold">Abonnements</th>
              </tr>
            </thead>
            <tbody>
              {[...serie].reverse().map((p) => (
                <tr key={p.jour} className="border-t border-line">
                  <td className="px-3 py-1.5 whitespace-nowrap">{dayShort.format(asDate(p.jour))}</td>
                  <td className="px-3 py-1.5 text-right font-semibold">{formatEuros(p.total)}</td>
                  <td className="px-3 py-1.5 text-right">{formatEuros(p.pourboires)}</td>
                  <td className="px-3 py-1.5 text-right">{formatEuros(p.messages)}</td>
                  <td className="px-3 py-1.5 text-right">{formatEuros(p.abonnements)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div
          ref={boxRef}
          className="relative transition-opacity"
          style={{ height: PAD.top + plotH + AXIS_BAND, opacity: dimmed ? 0.45 : 1 }}
        >
          {width > 0 && n > 0 && (
            <svg
              width={width}
              height={PAD.top + plotH + AXIS_BAND}
              role="img"
              aria-label={`Courbe des gains par jour sur ${n} jours, ${formatEuros(total)} au total. Flèches gauche et droite pour lire chaque jour.`}
              tabIndex={0}
              onKeyDown={onKey}
              onFocus={() => setActive((a) => a ?? last)}
              onBlur={() => setActive(null)}
              onPointerMove={(e) => pick(e.clientX, e.currentTarget)}
              onPointerDown={(e) => pick(e.clientX, e.currentTarget)}
              // Au doigt, l'infobulle reste affichée après le toucher ; elle
              // disparaît quand on touche ailleurs.
              onPointerLeave={(e) => e.pointerType === "mouse" && setActive(null)}
              className="block touch-pan-y outline-none focus-visible:ring-2 focus-visible:ring-accent rounded-lg"
            >
              {/* Graduations : traits fins, discrets */}
              {ticks.map((t) => (
                <g key={t}>
                  <line x1={PAD.left} x2={PAD.left + plotW} y1={y(t)} y2={y(t)} stroke="var(--line)" strokeWidth={1} />
                  <text
                    x={PAD.left - 8}
                    y={y(t)}
                    dy="0.32em"
                    textAnchor="end"
                    fill="var(--muted)"
                    fontSize={12}
                    style={{ fontVariantNumeric: "tabular-nums" }}
                  >
                    {formatEurosRound(t)}
                  </text>
                </g>
              ))}
              {dateTicks.map((i) => (
                <text
                  key={i}
                  x={x(i)}
                  y={PAD.top + plotH + 18}
                  textAnchor={i === last ? "end" : i === 0 ? "start" : "middle"}
                  fill="var(--muted)"
                  fontSize={12}
                >
                  {i === last ? "Aujourd'hui" : dayShort.format(asDate(serie[i].jour))}
                </text>
              ))}

              {/* La courbe et son aire */}
              <path d={area} fill="var(--chart)" fillOpacity={0.1} />
              <path d={line} fill="none" stroke="var(--chart)" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />

              {/* Aujourd'hui : point et valeur */}
              <circle cx={x(last)} cy={y(serie[last].total)} r={4} fill="var(--chart)" stroke="var(--surface)" strokeWidth={2} />
              <text
                x={x(last) + 10}
                y={y(serie[last].total)}
                dy="0.32em"
                fill="var(--foreground)"
                fontSize={13}
                fontWeight={700}
              >
                {formatEurosRound(serie[last].total)}
              </text>

              {/* Le repère vertical qui suit le doigt ou la souris */}
              {tip && shown !== null && (
                <g pointerEvents="none">
                  <line
                    x1={x(shown)}
                    x2={x(shown)}
                    y1={PAD.top}
                    y2={PAD.top + plotH}
                    stroke="var(--muted)"
                    strokeWidth={1}
                  />
                  <circle cx={x(shown)} cy={y(tip.total)} r={5} fill="var(--chart)" stroke="var(--surface)" strokeWidth={2} />
                </g>
              )}
            </svg>
          )}

          {tip && shown !== null && (
            <div
              role="status"
              className="pointer-events-none absolute z-10 rounded-xl border border-line bg-surface px-3 py-2 text-sm shadow-lg"
              style={{
                width: TIP_W,
                left: tipLeft,
                ...(tipLow ? { bottom: AXIS_BAND + 4 } : { top: PAD.top }),
              }}
            >
              <p className="text-xs text-muted first-letter:uppercase">{dayLong.format(asDate(tip.jour))}</p>
              <p className="text-lg font-bold">{formatEuros(tip.total)}</p>
              <dl className="mt-1 grid grid-cols-[1fr_auto] gap-x-3 tabular-nums">
                <dt className="text-muted">Pourboires</dt>
                <dd className="text-right">{formatEuros(tip.pourboires)}</dd>
                <dt className="text-muted">Messages</dt>
                <dd className="text-right">{formatEuros(tip.messages)}</dd>
                <dt className="text-muted">Abonnements</dt>
                <dd className="text-right">{formatEuros(tip.abonnements)}</dd>
              </dl>
            </div>
          )}
        </div>
      )}
    </figure>
  );
}
