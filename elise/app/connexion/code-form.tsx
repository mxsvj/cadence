"use client";

import { useActionState } from "react";
import { latestBirthdate } from "@/lib/age";
import { enterWithCode, type CodeState } from "./code-actions";

const field = "rounded-2xl border border-line bg-surface px-4 py-3 outline-none focus:border-accent";

// L'entrée de tout le monde : le code unique, un prénom, la date de naissance
// (18 ans minimum), et on arrive dans la conversation.
export function CodeForm({ initialCode }: { initialCode?: string }) {
  const [state, action, pending] = useActionState<CodeState, FormData>(enterWithCode, { code: initialCode });
  return (
    <form action={action} className="flex w-full flex-col gap-4">
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">Code d&apos;accès</span>
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
          className={`${field} text-center font-mono text-xl tracking-[0.2em] uppercase`}
        />
      </label>
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">Prénom ou pseudo</span>
        <input name="nom" required maxLength={60} autoComplete="given-name" defaultValue={state.name} className={field} />
      </label>
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">Date de naissance</span>
        <input
          name="naissance"
          type="date"
          required
          min="1900-01-01"
          max={latestBirthdate()}
          autoComplete="bday"
          defaultValue={state.birthdate}
          className={field}
        />
        <span className="text-sm text-muted">Réservé aux personnes majeures. Ni e-mail, ni mot de passe.</span>
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
