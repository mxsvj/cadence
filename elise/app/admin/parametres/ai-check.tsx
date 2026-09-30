"use client";

import { useState } from "react";
import { testAi, type AiCheck } from "./actions";

// « Tester l'IA » : une vraie réponse de chaque créatrice en ligne, sans rien
// enregistrer. Si ça coince, l'erreur exacte s'affiche.
export function AiCheckButton() {
  const [busy, setBusy] = useState(false);
  const [checks, setChecks] = useState<AiCheck[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setError(null);
    setChecks(null);
    try {
      const result = await testAi();
      if (result.ok) setChecks(result.checks);
      else setError(result.error);
    } catch {
      setError("Le test n'a pas pu aller au bout (plus d'une minute ?). Réessayez.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div>
        <button
          type="button"
          onClick={run}
          disabled={busy}
          className="rounded-full border border-line px-4 py-2 text-sm font-semibold disabled:opacity-60"
        >
          {busy ? "Test en cours…" : "Tester l'IA"}
        </button>
      </div>
      {error && (
        <p role="alert" className="break-words text-sm text-bad">
          {error}
        </p>
      )}
      {checks && (
        <ul className="flex flex-col gap-2 text-sm" aria-label="Résultat du test">
          {checks.map((c) => (
            <li key={c.creatrice} className="rounded-2xl bg-accent-soft px-4 py-3">
              <span className="font-semibold">
                {c.ok ? "✓" : "✗"} {c.creatrice}
              </span>
              <span className="text-muted">
                {" "}
                · {(c.ms / 1000).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} s{c.model ? ` · ${c.model}` : ""}
              </span>
              <span className="mt-1 block break-words">{c.ok ? `« ${c.text} »` : c.error}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
