"use client";

import { useState } from "react";

// Le préréglage d'emojis d'une personne : l'IA n'utilisera que ceux-là avec
// elle. Une grille pour les plus courants, et un champ pour coller n'importe
// quel autre emoji (tout le catalogue Unicode).

const GROUPS: { label: string; emojis: string }[] = [
  { label: "Sourires", emojis: "😊 🙂 😄 😁 😉 😌 🥰 😍 🤗 😇 😅 😂 🤭 😎 🤩 🥲 😢 😔 🫶 🙏" },
  { label: "Cœurs", emojis: "❤️ 🧡 💛 💚 💙 💜 🤍 🤎 🖤 💕 💞 💖 💗 💓 💫 ✨" },
  { label: "Nature", emojis: "🌸 🌷 🌹 🌻 🌼 🍀 🌿 🍃 🌙 ⭐ ☀️ 🌈 🌊 🔥 ❄️ 🐶 🐱 🦋" },
  { label: "Gourmandises", emojis: "☕ 🍵 🍷 🥂 🍰 🍫 🍪 🍓 🍒 🥐 🍕 🍝" },
  { label: "Activités", emojis: "🎶 🎵 🎧 📚 🎨 🎬 ✈️ 🏖️ 🏔️ 🚶 🧘 ⚽ 🎮 🎁 🎉" },
  { label: "Gestes", emojis: "👋 👍 👏 🙌 🤞 ✌️ 💪 🤝 🫂 👀" },
];

/** Découpe une chaîne en emojis (graphèmes), sans les espaces. */
export function splitEmojis(value: string): string[] {
  const segmenter = new Intl.Segmenter("fr", { granularity: "grapheme" });
  return [...segmenter.segment(value)].map((s) => s.segment).filter((g) => g.trim() && /\p{Extended_Pictographic}|\p{Regional_Indicator}/u.test(g));
}

export function EmojiPicker({ value, onChange, id }: { value: string; onChange: (value: string) => void; id?: string }) {
  const [open, setOpen] = useState(false);
  const chosen = splitEmojis(value);

  function toggle(emoji: string) {
    const next = chosen.includes(emoji) ? chosen.filter((e) => e !== emoji) : [...chosen, emoji];
    onChange(next.join(" "));
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <input
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Aucun : l'IA reste sobre"
          aria-label="Emojis de cette personne"
          className="min-w-0 flex-1 rounded-xl border border-line bg-surface px-3 py-2 text-lg outline-none focus:border-accent"
        />
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          className="rounded-xl border border-line px-3 py-2 text-sm font-semibold hover:bg-accent-soft"
        >
          {open ? "Fermer" : "Choisir"}
        </button>
      </div>
      {open && (
        <div className="flex flex-col gap-2 rounded-xl border border-line bg-surface p-3">
          {GROUPS.map((g) => (
            <div key={g.label}>
              <p className="mb-1 text-xs font-semibold text-muted">{g.label}</p>
              <div className="flex flex-wrap gap-1">
                {g.emojis.split(" ").map((e) => (
                  <button
                    key={e}
                    type="button"
                    onClick={() => toggle(e)}
                    aria-pressed={chosen.includes(e)}
                    aria-label={`Emoji ${e}`}
                    className={`size-9 rounded-lg text-xl ${chosen.includes(e) ? "bg-accent-soft ring-2 ring-accent" : "hover:bg-accent-soft"}`}
                  >
                    {e}
                  </button>
                ))}
              </div>
            </div>
          ))}
          <p className="text-xs text-muted">Pour tout autre emoji, collez-le simplement dans le champ ci-dessus.</p>
        </div>
      )}
    </div>
  );
}
