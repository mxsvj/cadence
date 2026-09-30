"use client";

import { useState, useSyncExternalStore } from "react";
import { changeEntryCode, type EntryCode } from "./code-actions";

const noop = () => () => {};

// Le code unique pour entrer et parler à l'IA : à donner à tous ceux qui testent.
export function EntryCodeCard({ initial }: { initial: EntryCode | null }) {
  const [current, setCurrent] = useState(initial);
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const origin = useSyncExternalStore(noop, () => window.location.origin, () => "");

  if (!current) {
    return <p className="text-sm text-muted">Le code arrive quand la base est à jour : relancez supabase/schema.sql dans Supabase.</p>;
  }
  const link = `${origin}/connexion?code=${current.code}`;

  async function copy() {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
    } catch {
      setNotice("Copie impossible : sélectionnez le lien et copiez-le à la main.");
    }
  }

  async function change() {
    setBusy(true);
    setNotice(null);
    const result = await changeEntryCode();
    setBusy(false);
    setConfirm(false);
    if (!result.ok) return setNotice(result.error);
    setCurrent({ code: result.code, change_le: result.change_le });
    setCopied(false);
    setNotice("Nouveau code en place : l'ancien ne marche plus.");
  }

  return (
    <div className="flex flex-col gap-3">
      <output data-code={current.code} className="font-mono text-3xl font-bold tracking-[0.2em]">
        {current.code}
      </output>
      <p className="break-all text-sm">
        Le lien, qui remplit le code tout seul : <span className="font-semibold">{link}</span>
      </p>
      <div className="flex flex-wrap items-center gap-2">
        <button type="button" onClick={copy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white">
          {copied ? "Lien copié" : "Copier le lien"}
        </button>
        {confirm ? (
          <>
            <button
              type="button"
              onClick={change}
              disabled={busy}
              className="rounded-full border border-bad px-4 py-2 text-sm font-bold text-bad disabled:opacity-60"
            >
              Oui, changer le code
            </button>
            <button type="button" onClick={() => setConfirm(false)} className="px-2 py-2 text-sm text-muted underline">
              Annuler
            </button>
          </>
        ) : (
          <button type="button" onClick={() => setConfirm(true)} className="rounded-full border border-line px-4 py-2 text-sm font-semibold">
            Changer le code
          </button>
        )}
      </div>
      {confirm && (
        <p className="text-xs text-muted">
          L&apos;ancien code ne marchera plus pour entrer. Les personnes déjà entrées restent connectées, avec leurs conversations.
        </p>
      )}
      {notice && (
        <p role="status" className="text-sm">
          {notice}
        </p>
      )}
    </div>
  );
}
