"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/admin", label: "Tableau de bord" },
  { href: "/admin/messages", label: "Messages" },
  { href: "/admin/ia", label: "IA" },
  { href: "/admin/contenus", label: "Contenus" },
];

export function AdminNav() {
  const path = usePathname();
  return (
    <nav
      aria-label="Espace de l'équipe"
      className="sticky top-0 z-20 border-b border-line bg-background/95 pt-[env(safe-area-inset-top)] backdrop-blur"
    >
      {/* Hauteur fixe (3,5 rem) : la messagerie s'en sert pour occuper le reste de l'écran. */}
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-1 overflow-x-auto px-3 sm:px-6">
        {TABS.map((t) => {
          const active = t.href === "/admin" ? path === "/admin" : path.startsWith(t.href);
          return (
            <Link
              key={t.href}
              href={t.href}
              aria-current={active ? "page" : undefined}
              className={`shrink-0 rounded-full px-4 py-2 text-sm font-semibold ${
                active ? "bg-accent text-white" : "text-muted hover:bg-accent-soft hover:text-foreground"
              }`}
            >
              {t.label}
            </Link>
          );
        })}
        <Link href="/" className="ml-auto shrink-0 px-3 py-2 text-sm text-muted underline underline-offset-4">
          Conversation
        </Link>
      </div>
    </nav>
  );
}
