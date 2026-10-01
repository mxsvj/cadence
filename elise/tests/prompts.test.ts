import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { getFirstMessage, getPersona } from "../lib/persona";
import { chatSystemPrompt, cleanReply, formatNow, transcript } from "../lib/prompts";

describe("persona", () => {
  it("contient la fiche complète", () => {
    assert.match(getPersona(), /^# Règles de base/);
  });
  it("extrait le premier message, en paragraphes et sans retours à la ligne parasites", () => {
    const first = getFirstMessage();
    assert.match(first, /^Bonjour, je suis Élise\./);
    assert.match(getFirstMessage("Chloé"), /^Bonjour, je suis Chloé\./);
    assert.match(first, /appelle \?$/);
    assert.ok(!first.includes("##"));
    for (const paragraph of first.split("\n\n")) assert.ok(!paragraph.includes("\n"));
  });
});

describe("chatSystemPrompt : ce que le modèle reçoit", () => {
  const now = new Date("2026-09-28T19:14:00Z");

  it("met la persona, la fiche, le résumé et la date", () => {
    const system = chatSystemPrompt({
      base: "PERSONA",
      facts: ["Se prénomme Karim.", "A un chat."],
      summary: "Ils ont parlé de son déménagement.",
      now,
    });
    // Le jour d'abord (l'IA se trompait de jour), puis les règles de base.
    assert.ok(system.startsWith("## Maintenant"));
    assert.ok(system.indexOf("PERSONA") < system.indexOf("## Ton personnage"));
    assert.match(system, /- Se prénomme Karim\.\n- A un chat\./);
    assert.match(system, /Ils ont parlé de son déménagement\./);
    assert.match(system, /lundi 28 septembre 2026 à 21 h 14/);
  });

  it("dit clairement quand on ne sait encore rien", () => {
    const system = chatSystemPrompt({ base: "P", facts: [], summary: null, now });
    assert.match(system, /Tu ne sais encore rien/);
    assert.match(system, /Pas encore de résumé/);
  });
});

describe("outils", () => {
  it("formatNow donne l'heure de Paris", () => {
    assert.equal(formatNow(new Date("2026-01-05T08:03:00Z")), "lundi 5 janvier 2026 à 9 h 03");
  });
  it("transcript distingue les deux voix", () => {
    assert.equal(
      transcript([
        { role: "assistant", content: "Bonjour" },
        { role: "user", content: " Salut " },
      ]),
      "Élise : Bonjour\n\nLa personne : Salut",
    );
  });
  it("cleanReply retire le gras et les titres", () => {
    assert.equal(cleanReply("## Titre\nC'est **très** bien."), "Titre\nC'est très bien.");
  });
  it("cleanReply coupe une réponse démesurée", () => {
    const reply = cleanReply("a".repeat(10_000));
    assert.equal(reply.length, 4001);
    assert.ok(reply.endsWith("…"));
  });
});
