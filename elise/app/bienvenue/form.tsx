"use client";

import { useActionState } from "react";
import { latestBirthdate } from "@/lib/age";
import { saveProfile, type ProfileState } from "./actions";

export function ProfileForm({ name, birthdate }: { name?: string; birthdate?: string }) {
  const [state, action, pending] = useActionState<ProfileState, FormData>(saveProfile, { name, birthdate });
  return (
    <form action={action} className="flex w-full flex-col gap-4">
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
        <span className="text-sm text-muted">Elle ne pourra plus être modifiée ensuite.</span>
      </label>
      {state.error && (
        <p role="alert" className="rounded-2xl bg-accent-soft px-4 py-3 text-sm">
          {state.error}
        </p>
      )}
      <button
        type="submit"
        disabled={pending}
        className="mt-1 rounded-2xl bg-accent px-4 py-3 font-bold text-white transition-opacity disabled:opacity-60"
      >
        {pending ? "Un instant…" : "Continuer"}
      </button>
    </form>
  );
}
