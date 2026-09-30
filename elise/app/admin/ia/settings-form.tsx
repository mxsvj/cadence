"use client";

import Link from "next/link";
import { useState } from "react";
import type { AiMode } from "@/lib/settings";
import { saveSettings } from "./actions";

const MODES: { value: AiMode; title: string; text: string }[] = [
  { value: "auto", title: "Automatique", text: "L'IA répond à tout le monde, tout de suite." },
  { value: "hybride", title: "Hybride", text: "L'IA ne répond qu'aux personnes cochées ; l'équipe répond aux autres." },
  { value: "manuel", title: "Manuel", text: "L'IA est coupée : l'équipe répond à tout, depuis l'onglet Messages." },
];

const card = "flex flex-col gap-4 rounded-3xl border border-line bg-surface p-5";

export type CreatorChoice = { id: number; name: string; details: string; active: boolean };

export function AiSettingsForm({ mode: initialMode, creators }: { mode: AiMode; creators: CreatorChoice[] }) {
  const [mode, setMode] = useState<AiMode>(initialMode);
  const [online, setOnline] = useState<number[]>(creators.filter((c) => c.active).map((c) => c.id));
  const [notice, setNotice] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setNotice(null);
    const result = await saveSettings({ mode, online });
    setSaving(false);
    setNotice(result.ok ? "Réglages enregistrés. Ils valent dès le prochain message." : result.error);
  }

  return (
    <form onSubmit={submit} className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 pb-28 sm:px-6">
      <header>
        <h1 className="font-serif text-3xl">IA</h1>
        <p className="text-sm text-muted">Qui répond, et quelles créatrices sont en ligne.</p>
      </header>

      {/* Le mode */}
      <section className={card} aria-labelledby="titre-mode">
        <h2 id="titre-mode" className="font-bold">
          Qui répond
        </h2>
        <div className="grid gap-3 sm:grid-cols-3" role="radiogroup" aria-labelledby="titre-mode">
          {MODES.map((m) => (
            <label
              key={m.value}
              className={`flex cursor-pointer flex-col gap-1 rounded-2xl border p-4 ${
                mode === m.value ? "border-accent bg-accent-soft" : "border-line"
              }`}
            >
              <span className="flex items-center gap-2 font-semibold">
                <input
                  type="radio"
                  name="mode"
                  value={m.value}
                  checked={mode === m.value}
                  onChange={() => setMode(m.value)}
                  className="accent-[var(--accent)]"
                />
                {m.title}
              </span>
              <span className="text-sm text-muted">{m.text}</span>
            </label>
          ))}
        </div>
        <p className="text-xs text-muted">
          Dans tous les cas, chaque réponse est marquée pour la personne : « IA » ou « Équipe ».
        </p>
      </section>

      {/* Les créatrices en ligne */}
      <section className={card} aria-labelledby="titre-creatrices">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 id="titre-creatrices" className="font-bold">
            Créatrices en ligne
          </h2>
          <Link href="/admin/creatrices/nouvelle" className="rounded-full border border-line px-4 py-1.5 text-sm font-semibold">
            Créer une créatrice
          </Link>
        </div>
        <p className="text-sm text-muted">
          Les personnes choisissent avec laquelle parler. Chaque conversation est séparée des autres : ses messages,
          ce que l&apos;IA sait de la personne, son script et ses offres. Une seule en ligne : on arrive directement
          chez elle.
        </p>
        <div className="flex flex-col gap-2">
          {creators.map((c) => {
            const on = online.includes(c.id);
            return (
              <label
                key={c.id}
                className={`flex cursor-pointer items-center gap-3 rounded-2xl border p-3 ${on ? "border-accent bg-accent-soft" : "border-line"}`}
              >
                <input
                  type="checkbox"
                  checked={on}
                  onChange={() => setOnline((list) => (on ? list.filter((id) => id !== c.id) : [...list, c.id]))}
                  className="size-4 accent-[var(--accent)]"
                  aria-label={`${c.name} en ligne`}
                />
                <span className="min-w-0 flex-1">
                  <span className="block font-semibold">{c.name}</span>
                  {c.details && <span className="block text-sm text-muted">{c.details}</span>}
                </span>
                <span className={`shrink-0 text-xs font-bold ${on ? "text-accent" : "text-muted"}`}>{on ? "En ligne" : "Hors ligne"}</span>
              </label>
            );
          })}
        </div>
        <p className="text-xs text-muted">
          Hors ligne, une créatrice ne répond plus et n&apos;apparaît plus dans le choix ; ses conversations restent
          lisibles par l&apos;équipe. Profil, premier message et réglages par personne : onglet Créatrices.
        </p>
      </section>

      {/* Juste au-dessus de la barre d'onglets. */}
      <div className="fixed inset-x-0 bottom-[calc(4rem+env(safe-area-inset-bottom))] z-10 border-t border-line bg-background/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center gap-3">
          <button type="submit" disabled={saving} className="rounded-full bg-accent px-5 py-2.5 font-bold text-white disabled:opacity-60">
            {saving ? "Enregistrement…" : "Enregistrer les réglages"}
          </button>
          {notice && (
            <p role="status" className="text-sm text-muted">
              {notice}
            </p>
          )}
        </div>
      </div>
    </form>
  );
}
