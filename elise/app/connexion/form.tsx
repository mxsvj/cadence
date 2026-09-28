"use client";

import { useActionState, useState } from "react";
import { latestBirthdate } from "@/lib/age";
import { authenticate, type AuthState } from "./actions";

export function AuthForm() {
  const [mode, setMode] = useState<"connexion" | "inscription">("connexion");
  const [state, action, pending] = useActionState<AuthState, FormData>(authenticate, {});
  const signingUp = mode === "inscription";

  return (
    <form action={action} className="flex w-full flex-col gap-4">
      <input type="hidden" name="mode" value={mode} />

      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">Adresse e-mail</span>
        <input
          name="email"
          type="email"
          required
          autoComplete="email"
          inputMode="email"
          defaultValue={state.email}
          className="rounded-2xl border border-line bg-surface px-4 py-3 outline-none focus:border-accent"
        />
      </label>

      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">Mot de passe</span>
        <input
          name="password"
          type="password"
          required
          minLength={6}
          autoComplete={signingUp ? "new-password" : "current-password"}
          className="rounded-2xl border border-line bg-surface px-4 py-3 outline-none focus:border-accent"
        />
        {signingUp && <span className="text-sm text-muted">Au moins 6 caractères.</span>}
      </label>

      {signingUp && (
        <>
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold">Prénom ou pseudo</span>
            <input
              name="nom"
              required
              maxLength={60}
              autoComplete="given-name"
              defaultValue={state.name}
              className="rounded-2xl border border-line bg-surface px-4 py-3 outline-none focus:border-accent"
            />
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
              className="rounded-2xl border border-line bg-surface px-4 py-3 outline-none focus:border-accent"
            />
            <span className="text-sm text-muted">Élise est réservée aux personnes de 18 ans et plus.</span>
          </label>
        </>
      )}

      {state.error && (
        <p role="alert" className="rounded-2xl bg-accent-soft px-4 py-3 text-sm">
          {state.error}
        </p>
      )}
      {state.info && (
        <p role="status" className="rounded-2xl border border-line bg-surface px-4 py-3 text-sm">
          {state.info}
        </p>
      )}

      <button
        type="submit"
        disabled={pending}
        className="mt-1 rounded-2xl bg-accent px-4 py-3 font-bold text-white transition-opacity disabled:opacity-60"
      >
        {pending ? "Un instant…" : signingUp ? "Créer mon compte" : "Me connecter"}
      </button>

      <button
        type="button"
        onClick={() => setMode(signingUp ? "connexion" : "inscription")}
        className="text-sm text-muted underline underline-offset-4"
      >
        {signingUp ? "J'ai déjà un compte : me connecter" : "Première visite ? Créer un compte"}
      </button>
    </form>
  );
}
