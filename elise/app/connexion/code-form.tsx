"use client";

import { useActionState } from "react";
import { enterWithCode, type CodeState } from "./code-actions";

// L'entrée des clients : leur code personnel, comme une carte de médiathèque.
export function CodeForm({ initialCode }: { initialCode?: string }) {
  const [state, action, pending] = useActionState<CodeState, FormData>(enterWithCode, { code: initialCode });
  return (
    <form action={action} className="flex w-full flex-col gap-4">
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">Votre code d&apos;accès</span>
        <input
          name="code"
          required
          defaultValue={state.code}
          placeholder="ABCD-EFGH"
          autoComplete="off"
          autoCapitalize="characters"
          autoCorrect="off"
          spellCheck={false}
          maxLength={20}
          className="rounded-2xl border border-line bg-surface px-4 py-3 text-center font-mono text-xl tracking-[0.2em] uppercase outline-none focus:border-accent"
        />
        <span className="text-sm text-muted">Le code que vous avez reçu. Pas besoin d&apos;e-mail ni de mot de passe.</span>
      </label>
      {state.error && (
        <p role="alert" className="rounded-2xl bg-accent-soft px-4 py-3 text-sm">
          {state.error}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="rounded-2xl bg-accent px-4 py-3 font-bold text-white transition-opacity disabled:opacity-60"
      >
        {pending ? "Un instant…" : "Entrer"}
      </button>
    </form>
  );
}
