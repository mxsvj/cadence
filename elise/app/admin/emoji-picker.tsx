"use client";

import { useId, useState } from "react";
import { EMOJI_GROUPS, MAX_EMOJIS, cleanEmojis, splitEmojis, type EmojiMode } from "@/lib/emojis";

// Les emojis d'une créatrice avec une personne : au choix de l'IA selon la
// discussion, seulement ceux qu'on choisit (tout le catalogue, rangé comme
// sur un téléphone, et un champ pour coller n'importe quel autre), ou aucun.

const MODES: { value: EmojiMode; label: string; hint: string }[] = [
  { value: "libre", label: "Au choix de l'IA", hint: "Elle prend ceux qui vont avec la discussion, sans en abuser." },
  { value: "choisis", label: "Seulement ceux que je choisis", hint: "Elle pioche dans votre liste, selon la discussion." },
  { value: "aucun", label: "Aucun emoji", hint: "Des messages sans emoji." },
];

export function EmojiChoice({
  who,
  mode,
  emojis,
  onChange,
}: {
  /** Le prénom de la personne, pour les libellés. */
  who: string;
  mode: EmojiMode;
  emojis: string;
  onChange: (mode: EmojiMode, emojis: string) => void;
}) {
  const name = useId();
  const [group, setGroup] = useState(0);
  const [paste, setPaste] = useState("");
  const chosen = splitEmojis(emojis);

  function toggle(emoji: string) {
    if (chosen.includes(emoji)) return onChange("choisis", chosen.filter((e) => e !== emoji).join(" "));
    if (chosen.length >= MAX_EMOJIS) return;
    onChange("choisis", [...chosen, emoji].join(" "));
  }

  function addPasted() {
    onChange("choisis", cleanEmojis(`${emojis} ${paste}`));
    setPaste("");
  }

  return (
    <fieldset className="flex min-w-0 flex-col gap-2">
      <legend className="sr-only">Emojis avec {who}</legend>
      <div className="grid gap-1.5 sm:grid-cols-3">
        {MODES.map((m) => (
          <label
            key={m.value}
            className={`flex cursor-pointer items-start gap-2 rounded-xl border p-2.5 text-sm ${
              mode === m.value ? "border-accent bg-accent-soft" : "border-line"
            }`}
          >
            <input
              type="radio"
              name={name}
              checked={mode === m.value}
              onChange={() => onChange(m.value, emojis)}
              className="mt-1 accent-[var(--accent)]"
            />
            <span>
              <span className="font-semibold">{m.label}</span>
              <span className="block text-xs text-muted">{m.hint}</span>
            </span>
          </label>
        ))}
      </div>

      {mode === "choisis" && (
        <div className="flex min-w-0 flex-col gap-3 rounded-xl border border-line p-3">
          <div className="flex flex-wrap items-center gap-1" aria-label={`Emojis choisis pour ${who}`} role="group">
            {chosen.length ? (
              <>
                {chosen.map((e) => (
                  <button
                    key={e}
                    type="button"
                    onClick={() => toggle(e)}
                    aria-label={`Retirer ${e}`}
                    className="rounded-lg bg-accent-soft px-1.5 py-0.5 text-xl"
                  >
                    {e}
                  </button>
                ))}
                <button type="button" onClick={() => onChange("choisis", "")} className="ml-auto px-1 text-xs text-muted underline">
                  Tout retirer
                </button>
              </>
            ) : (
              <span className="text-sm text-muted">Touchez les emojis ci-dessous pour les ajouter à la liste.</span>
            )}
          </div>

          <div role="tablist" aria-label="Familles d'emojis" className="flex gap-1 overflow-x-auto pb-1">
            {EMOJI_GROUPS.map((g, i) => (
              <button
                key={g.label}
                type="button"
                role="tab"
                aria-selected={i === group}
                onClick={() => setGroup(i)}
                className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${
                  i === group ? "bg-accent text-white" : "border border-line"
                }`}
              >
                {g.label}
              </button>
            ))}
          </div>
          <div role="tabpanel" className="grid grid-cols-8 gap-1 sm:grid-cols-12">
            {EMOJI_GROUPS[group].emojis.split(" ").map((e) => (
              <button
                key={e}
                type="button"
                onClick={() => toggle(e)}
                aria-pressed={chosen.includes(e)}
                aria-label={`Emoji ${e}`}
                className={`aspect-square rounded-lg text-xl ${
                  chosen.includes(e) ? "bg-accent-soft ring-2 ring-accent" : "hover:bg-accent-soft"
                }`}
              >
                {e}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={paste}
              onChange={(e) => setPaste(e.target.value)}
              placeholder="Ou collez d'autres emojis ici"
              aria-label={`Autres emojis pour ${who}`}
              className="min-w-0 flex-1 rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent"
            />
            <button
              type="button"
              disabled={!paste.trim()}
              onClick={addPasted}
              className="rounded-xl border border-line px-3 py-2 text-sm font-semibold disabled:opacity-40"
            >
              Ajouter
            </button>
          </div>
          {chosen.length >= MAX_EMOJIS && <p className="text-xs text-muted">{MAX_EMOJIS} emojis au plus.</p>}
        </div>
      )}
    </fieldset>
  );
}
