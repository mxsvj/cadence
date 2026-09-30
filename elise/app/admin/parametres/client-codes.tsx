"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { timeAgo } from "@/lib/dashboard";
import { createClientCode, removeClientCode, renewClientCode } from "./code-actions";

export type ClientCode = {
  user_id: string;
  label: string;
  nom: string;
  hint: string;
  cree_le: string;
  utilise_le: string | null;
};

const input = "rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent";

// Les codes d'accès des clients, comme des cartes de médiathèque : l'équipe
// en crée un par client et le lui envoie (le code, ou le lien qui le remplit).
export function ClientCodes({ initial, outdated }: { initial: ClientCode[]; outdated: boolean }) {
  const router = useRouter();
  const [label, setLabel] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [fresh, setFresh] = useState<{ code: string; who: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const [confirm, setConfirm] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());

  // « utilisé il y a 3 min » reste juste sans recharger la page.
  useEffect(() => {
    const tick = window.setInterval(() => setNow(Date.now()), 30_000);
    return () => window.clearInterval(tick);
  }, []);

  const link = fresh ? `${window.location.origin}/connexion?code=${fresh.code}` : "";

  async function run<T extends { ok: boolean; error?: string }>(action: () => Promise<T>, onOk: (r: T) => void) {
    setBusy(true);
    setNotice(null);
    setCopied(false);
    const result = await action();
    setBusy(false);
    if (!result.ok) return setNotice(result.error ?? "L'action n'a pas abouti.");
    onOk(result);
    router.refresh();
  }

  function create(e: React.FormEvent) {
    e.preventDefault();
    const who = label.trim();
    void run(
      () => createClientCode(who),
      (r) => {
        setFresh({ code: (r as { code: string }).code, who: who || "ce client" });
        setLabel("");
      },
    );
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
    } catch {
      setNotice("Copie impossible : sélectionnez le lien et copiez-le à la main.");
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {outdated ? (
        <p className="text-sm text-muted">Les codes arrivent quand la base est à jour : relancez supabase/schema.sql dans Supabase.</p>
      ) : (
        <form onSubmit={create} className="flex flex-wrap items-end gap-2">
          <label className="flex min-w-48 flex-1 flex-col gap-1 text-sm">
            <span className="font-semibold">Prénom ou surnom du client</span>
            <input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              maxLength={60}
              placeholder="Pour vous y retrouver (facultatif)"
              className={input}
            />
          </label>
          <button type="submit" disabled={busy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-60">
            Créer un code
          </button>
        </form>
      )}

      {fresh && (
        <div role="status" className="flex flex-col gap-2 rounded-2xl bg-accent-soft p-4">
          <p className="text-sm">Le code de {fresh.who} :</p>
          <output data-code={fresh.code} className="font-mono text-3xl font-bold tracking-[0.2em]">
            {fresh.code}
          </output>
          <p className="break-all text-sm">
            Ou le lien, qui remplit le code tout seul : <span className="font-semibold">{link}</span>
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" onClick={copy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white">
              {copied ? "Lien copié" : "Copier le lien"}
            </button>
            <button type="button" onClick={() => setFresh(null)} className="text-sm text-muted underline">
              J&apos;ai noté le code
            </button>
          </div>
          <p className="text-xs text-muted">
            Copiez-le maintenant : il ne sera plus affiché. Ce code vaut une clé : ne l&apos;envoyez qu&apos;à cette personne.
          </p>
        </div>
      )}

      {notice && (
        <p role="alert" className="text-sm text-bad">
          {notice}
        </p>
      )}

      {initial.length > 0 && (
        <ul className="flex flex-col divide-y divide-line text-sm">
          {initial.map((c) => (
            <li key={c.user_id} className="flex flex-wrap items-center justify-between gap-2 py-2">
              <span className="min-w-0">
                <span className="font-semibold">{c.nom}</span>
                <span className="text-muted"> · code …{c.hint}</span>
                <span className="block text-xs text-muted" suppressHydrationWarning>
                  Créé {timeAgo(c.cree_le, now)} · {c.utilise_le ? `utilisé ${timeAgo(c.utilise_le, now)}` : "jamais utilisé"}
                </span>
              </span>
              <span className="flex shrink-0 gap-2">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() =>
                    run(
                      () => renewClientCode(c.user_id),
                      (r) => setFresh({ code: (r as { code: string }).code, who: c.nom }),
                    )
                  }
                  aria-label={`Nouveau code pour ${c.nom}`}
                  className="rounded-full border border-line px-3 py-1 text-xs font-semibold disabled:opacity-60"
                >
                  Nouveau code
                </button>
                {confirm === c.user_id ? (
                  <>
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => run(() => removeClientCode(c.user_id), () => setConfirm(null))}
                      aria-label={`Confirmer : désactiver le code de ${c.nom}`}
                      className="rounded-full border border-bad px-3 py-1 text-xs font-bold text-bad disabled:opacity-60"
                    >
                      Confirmer
                    </button>
                    <button type="button" onClick={() => setConfirm(null)} className="px-1 py-1 text-xs text-muted underline">
                      Annuler
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => setConfirm(c.user_id)}
                    aria-label={`Désactiver le code de ${c.nom}`}
                    className="rounded-full px-2 py-1 text-xs text-muted underline"
                  >
                    Désactiver
                  </button>
                )}
              </span>
              {confirm === c.user_id && (
                <p className="w-full text-xs text-muted">
                  {c.nom} ne pourra plus entrer, même avec un nouveau code (un téléphone déjà connecté l&apos;est encore au plus
                  une heure). Ses conversations restent.
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
