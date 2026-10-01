// Ce que l'IA reçoit pour prendre des nouvelles, et ce qu'on garde de sa
// réponse.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { absence, cleanRelance, relanceTask } from "../lib/relances";

describe("prendre des nouvelles : la consigne", () => {
  it("dit depuis combien de temps la personne n'est pas venue", () => {
    assert.equal(absence(20), "un jour");
    assert.equal(absence(50), "2 jours");
    assert.match(relanceTask(75), /n'est pas venue depuis 3 jours/);
  });

  it("interdit reproches, attachement, vente et histoires inventées", () => {
    const task = relanceTask(48);
    assert.match(task, /Aucun reproche, aucune culpabilité, aucune insistance/);
    assert.match(task, /tu m'as manqué/);
    assert.match(task, /Rien qui crée de l'attachement ou de la dépendance/);
    assert.match(task, /Aucune vente : jamais de contenu payant, de photo, de promotion, d'offre ni de balise/);
    // Comme une amie qui passe dans les messages privés : 10 à 15 mots au plus.
    assert.match(task, /amical et discret, 10 à 15 mots au plus/);
    assert.match(task, /Une petite pensée pour toi ✨/);
    assert.match(task, /sa vie en dehors d'ici compte plus que cette conversation/);
    assert.match(task, /n'invente pas d'événement de ta vie/);
  });
});

describe("prendre des nouvelles : la réponse", () => {
  it("retire toute balise d'offre et la mise en forme", () => {
    assert.equal(cleanRelance("Coucou ! **Comment** s'est passée ta randonnée ?\n[[PROPOSER prix=9]]"), "Coucou ! Comment s'est passée ta randonnée ?");
  });

  it("n'enregistre rien si la réponse est vide", () => {
    assert.equal(cleanRelance("  [[PROPOSER]] "), null);
  });
});
