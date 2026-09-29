"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { deleteCreator } from "./actions";

export type CreatorCard = { id: number; name: string; details: string; active: boolean };

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
        {creators.map((c) => (
          <li key={c.id} className="flex flex-col gap-3 rounded-2xl border border-line bg-surface p-4 sm:flex-row sm:items-center">
            <span aria-hidden className="flex size-12 shrink-0 items-center justify-center rounded-full bg-accent text-lg font-bold text-white">
              {c.name.charAt(0).toUpperCase()}
            </span>
            <span className="min-w-0 flex-1">
              <span className="flex flex-wrap items-center gap-2">
                <span className="font-semibold">{c.name}</span>
                {c.active && <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-bold text-accent">Incarnée par l&apos;IA</span>}
              </span>
              {c.details && <span className="block text-sm text-muted">{c.details}</span>}
            </span>
            <span className="flex shrink-0 flex-wrap items-center gap-2">
              <Link href={`/admin/creatrices/${c.id}`} className="rounded-lg border border-line px-3 py-1 text-sm font-semibold">
                Modifier
              </Link>
              {confirm === c.id ? (
                <>
                  <button type="button" onClick={() => remove(c.id)} className="rounded-lg bg-bad px-3 py-1 text-sm font-semibold text-white">
                    Oui, supprimer {c.name}
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
        ))}
      </ul>
      {notice && (
        <p role="status" className="text-sm text-muted">
          {notice}
        </p>
      )}
    </div>
  );
}
