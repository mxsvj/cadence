// Les emojis d'une créatrice avec chaque personne. Trois façons de faire :
// au choix de l'IA selon la discussion, seulement ceux d'une liste, ou aucun.
// Partagé entre les écrans de l'équipe et le serveur.

export type EmojiMode = "libre" | "choisis" | "aucun";
export const EMOJI_MODES: readonly EmojiMode[] = ["libre", "choisis", "aucun"];
export const MAX_EMOJIS = 60;

export const isEmojiMode = (v: unknown): v is EmojiMode => EMOJI_MODES.includes(v as EmojiMode);

/**
 * Tout le catalogue, rangé comme sur un téléphone. Rien d'ambigu ni de
 * sexuel : ces emojis-là sont aussi refusés s'ils sont collés à la main.
 */
export const EMOJI_GROUPS: { label: string; emojis: string }[] = [
  {
    label: "Sourires",
    emojis:
      "😊 🙂 😀 😃 😄 😁 😆 😅 😂 🤣 🥲 ☺️ 😇 🙃 😉 😌 😍 🥰 😘 😗 😙 😚 😋 😛 😜 🤪 😝 🤗 🤭 🫢 🤫 🤔 🫡 🤐 🤨 😐 😑 😶 🫥 😏 😒 🙄 😬 😮‍💨 😔 😪 😴 🥱 🥶 🥴 😵‍💫 🤯 🤠 🥳 🥸 😎 🤓 🧐 😕 🫤 😟 🙁 😮 😯 😲 😳 🥺 🥹 😦 😧 😨 😰 😥 😢 😭 😱 😖 😣 😞 😓 😩 😫 😤 😠 😡 😈 👻 🤖 😺 😸 😹 😻 😼 🙈 🙉 🙊",
  },
  {
    label: "Cœurs",
    emojis: "❤️ 🧡 💛 💚 💙 🩵 💜 🤎 🖤 🩶 🤍 🩷 💕 💞 💓 💗 💖 💘 💝 💟 ❣️ 💔 ❤️‍🔥 ❤️‍🩹 💌 ✨ 💫",
  },
  {
    label: "Gestes",
    emojis: "👋 🤚 🖐️ ✋ 🖖 👌 🤌 🤏 ✌️ 🤞 🫰 🤟 🤘 🤙 👈 👉 👆 👇 ☝️ 👍 👎 ✊ 👊 🤛 🤜 👏 🙌 🫶 👐 🤲 🤝 🙏 ✍️ 💪 👀 🫂",
  },
  {
    label: "Personnes",
    emojis: "💁‍♀️ 🙋‍♀️ 🙆‍♀️ 🙅‍♀️ 🤷‍♀️ 🤦‍♀️ 🙇‍♀️ 🧘‍♀️ 🚶‍♀️ 🏃‍♀️ 💃 🕺 👯‍♀️ 🧑‍🍳 🧑‍🎨 🧑‍💻 🧑‍🎤 👩‍🌾 🧚 🧜‍♀️ 🦸‍♀️ 👸 🤶 🎅",
  },
  {
    label: "Animaux",
    emojis: "🐶 🐱 🐭 🐹 🐰 🦊 🐻 🐼 🐨 🐯 🦁 🐮 🐷 🐸 🐵 🐔 🐧 🐦 🐤 🦆 🦉 🐴 🦄 🐝 🦋 🐌 🐞 🐢 🐙 🐬 🐳 🐠 🦀 🦔 🐿️ 🦩 🦚 🐾",
  },
  {
    label: "Nature",
    emojis: "🌸 🌷 🌹 🥀 🌺 🌻 🌼 💐 🌱 🌿 ☘️ 🍀 🍃 🍂 🍁 🌳 🌲 🌴 🌵 🌾 🍄 🌍 🌙 🌛 ⭐ 🌟 ☀️ 🌤️ ⛅ 🌧️ ⛈️ 🌈 ❄️ ☃️ 🔥 💧 🌊",
  },
  {
    label: "Cuisine",
    emojis: "🍎 🍐 🍊 🍋 🍌 🍉 🍇 🍓 🫐 🍒 🥭 🍍 🥥 🥝 🥑 🥐 🥖 🧀 🍳 🥞 🧇 🍔 🍟 🍕 🌮 🥗 🍝 🍜 🍣 🍱 🍰 🎂 🧁 🍫 🍬 🍭 🍮 🍪 🍩 🍯",
  },
  {
    label: "Boissons",
    emojis: "☕ 🍵 🧋 🥤 🧃 🥛 🍷 🥂 🍾 🍺 🍻 🍸 🍹 🥃",
  },
  {
    label: "Loisirs",
    emojis: "⚽ 🏀 🏈 ⚾ 🎾 🏐 🏉 🏓 🏸 ⛳ 🎣 🎿 🏂 🚴 🏊 🧗 🧘 🎨 🎭 🎬 🎤 🎧 🎼 🎹 🥁 🎷 🎺 🎸 🎻 🎲 ♟️ 🎯 🎮 🧩 📚 📖 ✏️ 🧶 🧵 📷",
  },
  {
    label: "Voyages",
    emojis: "✈️ 🚗 🚕 🚌 🚲 🛵 🚂 🚢 ⛵ 🚀 🗺️ 🧭 🏔️ ⛰️ 🏕️ 🏖️ 🏝️ 🏜️ 🏛️ 🏰 🗼 🗽 ⛲ 🎡 🎢 🌅 🌄 🌇 🌃 🌉 🏠 🏡",
  },
  {
    label: "Fêtes et objets",
    emojis: "🎁 🎈 🎉 🎊 🎀 🕯️ 💡 📱 💻 ⌚ 📸 📺 📻 ⏰ ⌛ 🔑 🛋️ 🛁 🧸 🪴 🎄 🎃 🎆 🎇 ✉️ 📝 📅 🏆 🥇 👑 💎 👗 👠 👜 🕶️ 🧣 🧤 💄",
  },
  {
    label: "Symboles",
    emojis: "✅ ✔️ ❌ ❓ ❗ ‼️ ⁉️ 💯 🔆 ♻️ ⚡ 💤 💬 💭 🎵 🎶 ➕ ➡️ ⬅️ 🔄 🆗 🆒 🆕 🔝 🔔 ♾️ ☮️ ☯️",
  },
];

/** Refusés même collés à la main : sous-entendus sexuels. */
const BLOCKED = new Set(["🍆", "🍑", "💦", "👅", "🔞", "🫦", "💋", "🥵", "👙"]);

/** Découpe une chaîne en emojis (un par caractère affiché), sans le reste. */
export function splitEmojis(value: string): string[] {
  const segmenter = new Intl.Segmenter("fr", { granularity: "grapheme" });
  return [...segmenter.segment(value)]
    .map((s) => s.segment)
    .filter((g) => g.trim() && /\p{Extended_Pictographic}|\p{Regional_Indicator}/u.test(g));
}

/** La liste enregistrée : des emojis seulement, sans doublon ni emoji refusé. */
export function cleanEmojis(value: unknown): string {
  const list = splitEmojis(typeof value === "string" ? value : "").filter((e) => !BLOCKED.has(e.replace(/️/g, "")));
  return [...new Set(list)].slice(0, MAX_EMOJIS).join(" ").slice(0, 400);
}

/** « au choix de l'IA », « 😊 🌸 » ou « aucun » : pour les listes de l'équipe. */
export function emojiSummary(mode: EmojiMode, emojis: string): string {
  if (mode === "libre") return "au choix de l'IA";
  if (mode === "choisis" && emojis.trim()) return emojis.trim();
  return "aucun";
}

/** Ce que l'IA reçoit sur les emojis, pour une personne. */
export function emojiInstruction(mode: EmojiMode | undefined, emojis: string | undefined, favorites?: string): string {
  const list = (emojis ?? "").trim();
  const own = cleanEmojis(favorites ?? "");
  const sparingly = "au plus un par message, et pas à chaque message";
  if ((mode ?? "libre") === "libre") {
    return own
      ? `- Emojis : de préférence les tiens (${own}), ou d'autres qui vont avec la discussion ; ${sparingly}.`
      : `- Emojis : à toi de choisir ceux qui vont avec la discussion et le ton de la personne ; ${sparingly}.`;
  }
  if (mode === "choisis" && list) {
    return `- Emojis à utiliser avec elle, uniquement ceux-là, selon la discussion (${sparingly}) : ${list}`;
  }
  return "- N'utilise aucun emoji avec elle.";
}
