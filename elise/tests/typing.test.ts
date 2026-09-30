// Le rythme des réponses (comme une personne qui tape), et l'heure de la personne.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { chatSystemPrompt, personSection, validTimeZone } from "../lib/prompts";
import { typingDelayMs } from "../lib/typing";

describe("le temps d'écrire une réponse", () => {
  // random = 0,5 : 2 s de réflexion, vitesse de frappe moyenne (3,5 caractères par seconde).
  const middle = { random: () => 0.5, setting: undefined };

  it("lire le message, réfléchir, puis taper à une quarantaine de mots par minute", () => {
    // « salut » se lit en 1 s ; 70 caractères se tapent en 20 s.
    assert.equal(typingDelayMs("x".repeat(70), { ...middle, incoming: "salut" }), 23_000);
    // Un long message reçu prend plus de temps à lire (200 caractères : 10 s, plafonné à 6).
    assert.equal(typingDelayMs("x".repeat(70), { ...middle, incoming: "y".repeat(200) }), 28_000);
  });

  it("un message deux fois plus long prend deux fois plus de temps à taper", () => {
    const short = typingDelayMs("x".repeat(100), middle) - 3000;
    const long = typingDelayMs("x".repeat(200), middle) - 3000;
    assert.ok(Math.abs(long - short * 2) <= 1, `${long} ≈ 2 × ${short}`);
  });

  it("une vitesse qui varie un peu, comme une vraie personne", () => {
    const slow = typingDelayMs("x".repeat(70), { random: () => 0, setting: undefined });
    const fast = typingDelayMs("x".repeat(70), { random: () => 0.999, setting: undefined });
    assert.ok(slow > fast);
    assert.ok(slow <= 2000 + 1000 + (70 / (3.5 * 0.85)) * 1000 + 1);
  });

  it("jamais moins de 3 secondes, jamais plus de 90", () => {
    assert.equal(typingDelayMs("ok", middle), 3571); // 1 s de lecture + 2 s de réflexion + 0,6 s pour le mot
    assert.equal(typingDelayMs("", { random: () => 0, setting: undefined }), 3000);
    assert.equal(typingDelayMs("x".repeat(2000), middle), 90_000);
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
