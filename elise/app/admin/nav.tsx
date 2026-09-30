"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAlerts } from "./alerts-store";

// Les onglets de l'équipe, en bas de l'écran comme dans une appli. La barre
// fait 4 rem (plus la marge de l'iPhone) : la mise en page et la messagerie
// s'en servent pour ne rien cacher dessous.

const icon = "size-6";
const stroke = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

const TABS = [
  {
    href: "/admin",
    label: "Tableau",
    name: "Tableau de bord",
    icon: (
      <svg viewBox="0 0 24 24" className={icon} {...stroke}>
        <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
      </svg>
    ),
  },
  {
    href: "/admin/messages",
    label: "Messages",
    name: "Messages",
    icon: (
      <svg viewBox="0 0 24 24" className={icon} {...stroke}>
        <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12Z" />
      </svg>
    ),
  },
  {
    href: "/admin/ia",
    label: "IA",
    name: "IA",
    icon: (
      <svg viewBox="0 0 24 24" className={icon} {...stroke}>
        <path d="M12 3v3M12 18v3M3 12h3M18 12h3M12 8l1.4 2.6L16 12l-2.6 1.4L12 16l-1.4-2.6L8 12l2.6-1.4Z" />
      </svg>
    ),
  },
  {
    href: "/admin/creatrices",
    label: "Créatrices",
    name: "Créatrices",
    icon: (
      <svg viewBox="0 0 24 24" className={icon} {...stroke}>
        <circle cx="12" cy="8" r="4" />
        <path d="M4 21a8 8 0 0 1 16 0" />
        <path d="m18.5 2.5.6 1.3 1.4.2-1 1 .2 1.4-1.2-.7-1.2.7.2-1.4-1-1 1.4-.2Z" />
      </svg>
    ),
  },
  {
    href: "/admin/contenus",
    label: "Contenus",
    name: "Contenus",
    icon: (
      <svg viewBox="0 0 24 24" className={icon} {...stroke}>
        <rect x="3" y="4" width="18" height="16" rx="2" />
        <path d="m3 16 5-5 4 4 3-3 6 6" />
        <circle cx="15.5" cy="8.5" r="1.5" />
      </svg>
    ),
  },
  {
    href: "/admin/parametres",
    label: "Paramètres",
    name: "Paramètres",
    icon: (
      <svg viewBox="0 0 24 24" className={icon} {...stroke}>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" />
      </svg>
    ),
  },
];

export function AdminNav() {
  const path = usePathname();
  // La pastille de l'onglet Messages : les alertes à traiter (rouge s'il y a une urgence).
  const { alerts } = useAlerts();
  const urgent = alerts.some((a) => a.kind === "urgence");
  return (
    <nav
      aria-label="Espace de l'équipe"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-background/95 pb-[env(safe-area-inset-bottom)] backdrop-blur"
    >
      <ul className="mx-auto grid h-16 max-w-2xl grid-cols-6">
        {TABS.map((t) => {
          const active = t.href === "/admin" ? path === "/admin" : path.startsWith(t.href);
          const badge = t.href === "/admin/messages" ? alerts.length : 0;
          return (
            <li key={t.href} className="min-w-0">
              <Link
                href={t.href}
                aria-label={badge ? `${t.name} (${badge} alerte${badge > 1 ? "s" : ""} à traiter)` : t.name}
                aria-current={active ? "page" : undefined}
                className={`flex h-full flex-col items-center justify-center gap-0.5 text-[11px] font-semibold ${
                  active ? "text-accent" : "text-muted hover:text-foreground"
                }`}
              >
                <span aria-hidden className="relative">
                  {t.icon}
                  {badge > 0 && (
                    <span
                      className={`absolute -top-1.5 -right-2.5 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-bold text-white ${
                        urgent ? "bg-bad" : "bg-accent"
                      }`}
                    >
                      {badge > 99 ? "99+" : badge}
                    </span>
                  )}
                </span>
                <span aria-hidden className="max-w-full truncate px-0.5">
                  {t.label}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
