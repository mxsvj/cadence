"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { deleteCreator } from "./actions";

export type CreatorCard = {
  id: number;
  /** Le prénom, ou null tant qu'il n'est pas rempli. */
  name: string | null;
  details: string;
  active: boolean;
  scripts: string[];
};

// Chaque créatrice est un bouton : on touche son nom pour revenir sur sa page,
// telle qu'on l'a laissée (tout s'y enregistre tout seul).
export function CreatorList({ creators }: { creators: CreatorCard[] }) {
  const router = useRouter();
  const [confirm, setConfirm] = useState<number | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function remove(id: number) {
    const result = await deleteCreator(id);
    setConfirm(null);
    setNotice(result.ok ? "Créatrice supprimée." : result.error);
    router.refresh();
  }

  if (!creators.length) {
    return (
      <p className="rounded-3xl border border-dashed border-line p-6 text-sm text-muted">
        Aucune créatrice pour l&apos;instant : l&apos;IA se présente sous le nom d&apos;Élise, avec son personnage par
        défaut. Créez-en une pour lui donner un profil complet.
      </p>
    );
  }
  return (
    <div className="flex flex-col gap-3">
      <ul className="flex flex-col gap-3">
        {creators.map((c) => {
          const name = c.name ?? "Sans prénom";
          return (
            <li key={c.id} className="flex flex-col gap-2 rounded-2xl border border-line bg-surface p-3 sm:flex-row sm:items-center">
              <Link
                href={`/admin/creatrices/${c.id}`}
                aria-label={`Créatrice ${name}`}
                className="flex min-w-0 flex-1 items-center gap-3 rounded-xl p-1 hover:bg-accent-soft"
              >
                <span aria-hidden className="flex size-12 shrink-0 items-center justify-center rounded-full bg-accent text-lg font-bold text-white">
                  {c.name ? c.name.charAt(0).toUpperCase() : "?"}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex flex-wrap items-center gap-2">
                    <span className="font-semibold">{name}</span>
                    {c.active && <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-bold text-accent">Incarnée par l&apos;IA</span>}
                    {!c.name && <span className="rounded-full border border-line px-2 py-0.5 text-xs text-muted">À compléter</span>}
                  </span>
                  {c.details && <span className="block text-sm text-muted">{c.details}</span>}
                  <span className="block text-xs text-muted">
                    {c.scripts.length ? `Scripts : ${c.scripts.join(", ")}` : "Aucun script à elle (onglet Contenus)"}
                  </span>
                </span>
                <span aria-hidden className="shrink-0 text-xl text-muted">
                  ›
                </span>
              </Link>
              <span className="flex shrink-0 flex-wrap items-center justify-end gap-2">
                {confirm === c.id ? (
                  <>
                    <button type="button" onClick={() => remove(c.id)} className="rounded-lg bg-bad px-3 py-1 text-sm font-semibold text-white">
                      Oui, supprimer {name}
                    </button>
                    <button type="button" onClick={() => setConfirm(null)} className="px-2 text-sm text-muted">
                      Annuler
                    </button>
                  </>
                ) : (
                  <button type="button" onClick={() => setConfirm(c.id)} className="px-2 py-1 text-sm text-bad underline">
                    Supprimer
                  </button>
                )}
              </span>
            </li>
          );
        })}
      </ul>
      {notice && (
        <p role="status" className="text-sm text-muted">
          {notice}
        </p>
      )}
    </div>
  );
}
