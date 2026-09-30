"use client";

import { bucketLabel, type DashboardData } from "@/lib/dashboard";

type Bucket = NonNullable<DashboardData["repartition"]>[number];

// La LTV en un coup d'œil : combien de clients ont dépensé combien au total.
// Une seule série, une seule couleur, la valeur au bout de chaque barre.
export function LtvChart({ buckets }: { buckets: Bucket[] }) {
  const total = buckets.reduce((s, b) => s + b.clients, 0);
  const max = Math.max(1, ...buckets.map((b) => b.clients));

  return (
    <figure className="flex min-w-0 flex-col gap-3">
      <figcaption>
        <span className="block font-bold">Clients par LTV</span>
        <span className="text-sm text-muted">Combien de clients ont dépensé combien, au total</span>
      </figcaption>
      {total === 0 ? (
        <p className="text-sm text-muted">Pas encore de client.</p>
      ) : (
        <ul className="flex flex-col gap-1">
          {buckets.map((b) => {
            const label = bucketLabel(b.min_cents, b.max_cents);
            const share = Math.round((b.clients / total) * 100);
            return (
              <li
                key={b.min_cents}
                aria-label={`${label} : ${b.clients} client${b.clients > 1 ? "s" : ""}, ${share} %`}
                className="grid grid-cols-[7rem_1fr] items-center gap-3 rounded-lg px-1 py-1.5 text-sm hover:bg-accent-soft"
              >
                <span aria-hidden className="text-muted">
                  {label}
                </span>
                <span aria-hidden className="flex min-w-0 items-center gap-2">
                  {b.clients > 0 && (
                    <span
                      className="h-4 shrink-0 rounded-r-[4px]"
                      style={{ width: `${(b.clients / max) * 60}%`, minWidth: 4, background: "var(--chart)" }}
                    />
                  )}
                  <span className="font-semibold tabular-nums">{b.clients}</span>
                  <span className="whitespace-nowrap text-muted tabular-nums">{share} %</span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </figure>
  );
}
