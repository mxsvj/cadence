// Le rythme des réponses (comme une personne qui tape), et l'heure de la personne.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { chatSystemPrompt, nowSection, personSection, validTimeZone } from "../lib/prompts";
import { typingDelayMs } from "../lib/typing";

describe("le temps d'écrire une réponse", () => {
  // random = 0,5 : 3,5 s de réflexion, vitesse de frappe moyenne (2,5 caractères par seconde).
  const middle = { random: () => 0.5, setting: undefined };

  it("lire le message, réfléchir, puis taper à une trentaine de mots par minute", () => {
    // « salut » se lit en 1,5 s (le minimum) ; 70 caractères se tapent en 28 s.
    assert.equal(typingDelayMs("x".repeat(70), { ...middle, incoming: "salut" }), 33_000);
    // Un long message reçu prend plus de temps à lire (200 caractères : 13 s, plafonné à 8).
    assert.equal(typingDelayMs("x".repeat(70), { ...middle, incoming: "y".repeat(200) }), 39_500);
  });

  it("un message deux fois plus long prend deux fois plus de temps à taper", () => {
    const short = typingDelayMs("x".repeat(100), middle) - 5000;
    const long = typingDelayMs("x".repeat(200), middle) - 5000;
    assert.ok(Math.abs(long - short * 2) <= 1, `${long} ≈ 2 × ${short}`);
  });

  it("une vitesse qui varie un peu, comme une vraie personne", () => {
    const slow = typingDelayMs("x".repeat(70), { random: () => 0, setting: undefined });
    const fast = typingDelayMs("x".repeat(70), { random: () => 0.999, setting: undefined });
    assert.ok(slow > fast);
    assert.ok(slow <= 1500 + 2000 + (70 / (2.5 * 0.85)) * 1000 + 1);
  });

  it("jamais moins de 4 secondes, jamais plus de 2 minutes", () => {
    assert.equal(typingDelayMs("ok", middle), 5800); // 1,5 s de lecture + 3,5 s de réflexion + 0,8 s pour le mot
    assert.equal(typingDelayMs("", { random: () => 0, setting: undefined }), 4000);
    assert.equal(typingDelayMs("x".repeat(2000), middle), 120_000);
  });

  it("HUMAN_TYPING=off : la réponse s'affiche dès qu'elle arrive", () => {
    assert.equal(typingDelayMs("x".repeat(70), { setting: "off" }), 0);
    assert.equal(typingDelayMs("x".repeat(70), { setting: " OFF " }), 0);
  });
});

describe("l'heure de la personne, celle de son téléphone", () => {
  const now = new Date("2026-09-28T19:14:00Z");

  it("accepte un vrai fuseau, refuse le reste", () => {
    assert.equal(validTimeZone("America/Toronto"), "America/Toronto");
    assert.equal(validTimeZone("Europe/Paris"), "Europe/Paris");
    // « UTC » : un ordinateur sans fuseau réglé, absent de la liste de la fiche.
    for (const bad of ["", "Mars/Olympus", "UTC", 42, null, "x".repeat(80)]) assert.equal(validTimeZone(bad), null, String(bad));
  });

  it("l'IA vit à son heure à elle", () => {
    const person = personSection({ timezone: "America/Toronto" }, now);
    assert.match(person, /Chez elle, nous sommes le lundi 28 septembre à 15:14 \(America\/Toronto\)\. C'est son heure qui compte/);
    const prompt = chatSystemPrompt({ base: "Règles.", person: { timezone: "America/Toronto" }, facts: [], summary: null, now });
    assert.match(prompt, /## Repères\n\nChez la personne, nous sommes le lundi 28 septembre 2026 à 15 h 14 \(America\/Toronto\)\./);
  });

  it("sans fuseau connu (ou un fuseau inventé) : l'heure de Paris", () => {
    for (const timezone of [undefined, "Mars/Olympus"]) {
      const prompt = chatSystemPrompt({ base: "Règles.", person: { timezone }, facts: [], summary: null, now });
      assert.match(prompt, /Chez la personne, nous sommes le lundi 28 septembre 2026 à 21 h 14 \(Europe\/Paris\)\./);
    }
  });
});

describe("le bon jour, la bonne heure", () => {
  // Jeudi 1er octobre 2026, 22 h 14 à Paris.
  const thursday = new Date("2026-10-01T20:14:00Z");

  it("en tête de la consigne : le jour, le moment de la journée, hier et demain", () => {
    const text = nowSection(thursday, "Europe/Paris");
    assert.match(text, /^## Maintenant\n\nChez la personne, nous sommes le jeudi 1 octobre 2026 à 22 h 14 \(Europe\/Paris\) : c'est le soir\./);
    assert.match(text, /Hier, c'était mercredi 30 septembre ; demain, ce sera vendredi 2 octobre\./);
    assert.match(text, /Ne parle jamais d'un jour qui n'est pas encore arrivé comme s'il était passé/);
    const prompt = chatSystemPrompt({ base: "# Règles", person: {}, facts: [], summary: null, now: thursday });
    assert.ok(prompt.startsWith("## Maintenant"));
    assert.match(prompt, /## Repères\n\n.+Rappel : on est jeudi\.$/);
  });

  it("à l'heure de la personne : à Toronto, c'est encore l'après-midi", () => {
    assert.match(nowSection(thursday, "America/Toronto"), /jeudi 1 octobre 2026 à 16 h 14 \(America\/Toronto\) : c'est l'après-midi/);
    assert.match(nowSection(new Date("2026-10-01T23:30:00Z"), "Europe/Paris"), /vendredi 2 octobre 2026 à 1 h 30 .+ c'est la nuit/);
  });

  it("dit depuis quand la personne n'avait pas écrit, si ça fait plus de deux heures", () => {
    const yesterday = new Date("2026-09-30T19:05:00Z");
    assert.match(nowSection(thursday, "Europe/Paris", yesterday), /Son message précédent date du mercredi 30 septembre 2026 à 21 h 05 : du temps a passé depuis\./);
    assert.doesNotMatch(nowSection(thursday, "Europe/Paris", new Date("2026-10-01T20:00:00Z")), /Son message précédent/);
  });
});
