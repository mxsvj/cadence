// Le rythme des réponses (comme une personne qui tape), et l'heure de la personne.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { chatSystemPrompt, personSection, validTimeZone } from "../lib/prompts";
import { typingDelayMs } from "../lib/typing";

describe("le temps d'écrire une réponse", () => {
  const at = (r: number) => () => r;

  it("lire, puis taper à environ 7 caractères par seconde", () => {
    const seventy = "x".repeat(70);
    assert.equal(typingDelayMs(seventy, at(0), undefined), 11_000); // 1 s pour lire + 10 s pour taper
    assert.equal(typingDelayMs(seventy, at(1), undefined), 12_500); // jusqu'à 2,5 s pour lire
  });

  it("jamais moins de 2 secondes, jamais plus de 20", () => {
    assert.equal(typingDelayMs("ok", at(0), undefined), 2000);
    assert.equal(typingDelayMs("x".repeat(2000), at(1), undefined), 20_000);
  });

  it("HUMAN_TYPING=off : la réponse s'affiche dès qu'elle arrive", () => {
    assert.equal(typingDelayMs("x".repeat(70), at(0), "off"), 0);
    assert.equal(typingDelayMs("x".repeat(70), at(0), " OFF "), 0);
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
